import java.util.*;

public class Ordenamientos {
    static double[] bubble(double[] a) {
        for (int fin = a.length - 1; fin > 0; fin--) {
            boolean cambio = false;
            for (int j = 0; j < fin; j++) if (a[j] > a[j+1]) {
                double v = a[j]; a[j] = a[j+1]; a[j+1] = v; cambio = true;
            }
            if (!cambio) break;
        }
        return a;
    }
    static double[] merge(double[] a) {
        int n = a.length;
        double[] aux = new double[n];
        for (long ancho = 1; ancho < n; ancho *= 2) {
            for (long ini = 0; ini < n; ini += 2*ancho) {
                int inicio = (int)ini, medio = (int)Math.min(ini+ancho,n);
                int fin = (int)Math.min(ini+2*ancho,n);
                int i = inicio, j = medio, k = inicio;
                while (i < medio && j < fin) aux[k++] = a[i] <= a[j] ? a[i++] : a[j++];
                while (i < medio) aux[k++] = a[i++];
                while (j < fin) aux[k++] = a[j++];
            }
            double[] cambio = a; a = aux; aux = cambio;
        }
        return a;
    }
    static class Nodo {
        double valor; int cantidad = 1; Nodo izq, der;
        Nodo(double valor) { this.valor = valor; }
    }
    static double[] tree(double[] a) {
        Nodo raiz = null;
        for (double valor : a) {
            if (raiz == null) { raiz = new Nodo(valor); continue; }
            Nodo actual = raiz;
            while (true) {
                if (valor == actual.valor) { actual.cantidad++; break; }
                if (valor < actual.valor) {
                    if (actual.izq == null) { actual.izq = new Nodo(valor); break; }
                    actual = actual.izq;
                } else {
                    if (actual.der == null) { actual.der = new Nodo(valor); break; }
                    actual = actual.der;
                }
            }
        }
        ArrayDeque<Nodo> pila = new ArrayDeque<>();
        Nodo actual = raiz; int i = 0;
        while (actual != null || !pila.isEmpty()) {
            while (actual != null) { pila.push(actual); actual = actual.izq; }
            actual = pila.pop();
            for (int c = 0; c < actual.cantidad; c++) a[i++] = actual.valor;
            actual = actual.der;
        }
        return a;
    }
    static void bajar(double[] a, int raiz, int fin) {
        while (2L*raiz+1 < fin) {
            int hijo = 2*raiz+1;
            if (hijo+1 < fin && a[hijo] < a[hijo+1]) hijo++;
            if (a[raiz] >= a[hijo]) break;
            double v = a[raiz]; a[raiz] = a[hijo]; a[hijo] = v; raiz = hijo;
        }
    }
    static double[] heap(double[] a) {
        for (int i = a.length/2-1; i >= 0; i--) bajar(a,i,a.length);
        for (int fin = a.length-1; fin > 0; fin--) {
            double v = a[0]; a[0] = a[fin]; a[fin] = v; bajar(a,0,fin);
        }
        return a;
    }
    static double[] counting(double[] a) {
        if (a.length == 0) return a;
        long min = Long.MAX_VALUE, max = Long.MIN_VALUE;
        for (double v : a) { long k = Math.round(v*100); min = Math.min(min,k); max = Math.max(max,k); }
        if (max-min > 1_000_000) throw new IllegalArgumentException("Rango excesivo");
        int[] cuentas = new int[(int)(max-min+1)];
        for (double v : a) {
            long k = Math.round(v*100);
            if (Math.abs(v*100-k) > 1e-7) throw new IllegalArgumentException("Se requieren centesimas");
            cuentas[(int)(k-min)]++;
        }
        int pos = 0;
        for (int i = 0; i < cuentas.length; i++)
            for (int c = 0; c < cuentas[i]; c++) a[pos++] = (i+min)/100.0;
        return a;
    }
    static double[] ordenar(String nombre, double[] a) {
        return switch(nombre) {
            case "bubble" -> bubble(a); case "merge" -> merge(a);
            case "tree" -> tree(a); case "heap" -> heap(a);
            case "counting" -> counting(a);
            default -> throw new IllegalArgumentException(nombre);
        };
    }
    static double[] generar(int n) {
        double[] a = new double[n]; long estado = 2026;
        for (int i = 0; i < n; i++) {
            estado = (1664525L*estado+1013904223L)&0xffffffffL;
            a[i] = ((estado%100001)-50000)/100.0;
        }
        return a;
    }
    static void pruebas() {
        double[][] casos = {{},{1},{3,2,1},{-1,0,-1,2},{1,2,3},{2.25,-1.5,0,2.25}};
        for (String nombre : List.of("bubble","merge","tree","heap","counting")) {
            for (double[] caso : casos) {
                double[] ref = caso.clone(); Arrays.sort(ref);
                if (!Arrays.equals(ordenar(nombre,caso.clone()),ref)) throw new AssertionError(nombre);
            }
            double[] caso = generar(500), ref = caso.clone(); Arrays.sort(ref);
            if (!Arrays.equals(ordenar(nombre,caso),ref)) throw new AssertionError(nombre);
        }
        System.out.println("35 pruebas Java correctas");
    }
    public static void main(String[] args) {
        if (args.length == 0 || args[0].equals("test")) { pruebas(); return; }
        String nombre = args[0]; int n = Integer.parseInt(args[1]);
        for (int w = 0; w < 5; w++) ordenar(nombre,generar(200));
        double[] a = generar(n); int[] cuentas = new int[100001];
        for (double v : a) cuentas[(int)Math.round(v*100)+50000]++;
        long inicio = System.nanoTime(); a = ordenar(nombre,a);
        double segundos = (System.nanoTime()-inicio)/1e9;
        boolean valido = a.length == n; double anterior = Double.NEGATIVE_INFINITY;
        for (double v : a) {
            if (v < anterior) valido = false;
            anterior = v; cuentas[(int)Math.round(v*100)+50000]--;
        }
        for (int c : cuentas) if (c != 0) valido = false;
        System.out.println("{\"segundos\":"+segundos+",\"valido\":"+valido+"}");
    }
}

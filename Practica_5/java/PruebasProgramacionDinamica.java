import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Queue;
import java.util.Random;

public final class PruebasProgramacionDinamica {
    private static int verificaciones = 0;

    private PruebasProgramacionDinamica() {}

    private static void igual(long esperado, long real, String caso) {
        if (esperado != real) {
            throw new AssertionError(caso + ": esperado=" + esperado + ", real=" + real);
        }
        verificaciones++;
    }

    private static void cierto(boolean condicion, String caso) {
        if (!condicion) throw new AssertionError(caso);
        verificaciones++;
    }

    private static void esperaError(Runnable accion, String caso) {
        try {
            accion.run();
        } catch (IllegalArgumentException esperado) {
            verificaciones++;
            return;
        }
        throw new AssertionError(caso + ": se esperaba IllegalArgumentException");
    }

    private static int mochilaExhaustiva(int[] pesos, int[] valores, int capacidad) {
        int mejor = 0;
        for (int mascara = 0; mascara < (1 << pesos.length); mascara++) {
            int pesoTotal = 0, valorTotal = 0;
            for (int i = 0; i < pesos.length; i++) {
                if ((mascara & (1 << i)) != 0) {
                    pesoTotal += pesos[i];
                    valorTotal += valores[i];
                }
            }
            if (pesoTotal <= capacidad) mejor = Math.max(mejor, valorTotal);
        }
        return mejor;
    }

    private static void verificarMochila(int[] pesos, int[] valores, int capacidad, int esperado) {
        igual(esperado, ProgramacionDinamica.mochilaRecursiva(pesos, valores, capacidad), "mochila recursiva");
        igual(esperado, ProgramacionDinamica.mochilaMemoizada(pesos, valores, capacidad), "mochila memoizada");
        igual(esperado, ProgramacionDinamica.mochilaTabla(pesos, valores, capacidad), "mochila tabulada");
    }

    private static void probarMochila() {
        verificarMochila(new int[0], new int[0], 0, 0);
        verificarMochila(new int[]{1}, new int[]{5}, 0, 0);
        verificarMochila(new int[]{3}, new int[]{7}, 2, 0);
        verificarMochila(new int[]{2, 3, 4}, new int[]{3, 4, 5}, 5, 7);
        verificarMochila(new int[]{10, 20, 30}, new int[]{60, 100, 120}, 50, 220);

        Random rng = new Random(2026);
        for (int ensayo = 0; ensayo < 25; ensayo++) {
            int n = rng.nextInt(9);
            int[] pesos = new int[n], valores = new int[n];
            for (int i = 0; i < n; i++) {
                pesos[i] = 1 + rng.nextInt(9);
                valores[i] = rng.nextInt(25);
            }
            int capacidad = rng.nextInt(25);
            verificarMochila(pesos, valores, capacidad, mochilaExhaustiva(pesos, valores, capacidad));
        }
        esperaError(() -> ProgramacionDinamica.mochilaTabla(new int[]{1}, new int[0], 1), "longitudes distintas");
        esperaError(() -> ProgramacionDinamica.mochilaTabla(new int[]{0}, new int[]{1}, 1), "peso cero");
        System.out.println("OK mochila 0/1");
    }

    private static int cambioMinimoBfs(int[] monedas, int cantidad) {
        int[] distancia = new int[cantidad + 1];
        Arrays.fill(distancia, -1);
        distancia[0] = 0;
        Queue<Integer> cola = new ArrayDeque<>();
        cola.add(0);
        while (!cola.isEmpty()) {
            int actual = cola.remove();
            for (int moneda : monedas) {
                int siguiente = actual + moneda;
                if (siguiente <= cantidad && distancia[siguiente] == -1) {
                    distancia[siguiente] = distancia[actual] + 1;
                    cola.add(siguiente);
                }
            }
        }
        return distancia[cantidad];
    }

    private static long formasExhaustivas(int[] monedas, int indice, int restante) {
        if (restante == 0) return 1;
        if (indice == monedas.length || restante < 0) return 0;
        long total = 0;
        for (int n = 0; n <= restante / monedas[indice]; n++) {
            total += formasExhaustivas(monedas, indice + 1, restante - n * monedas[indice]);
        }
        return total;
    }

    private static void verificarCambio(int[] monedas, int cantidad, int esperadoMin, long esperadoFormas) {
        igual(esperadoMin, ProgramacionDinamica.cambioMinimoRecursivo(monedas, cantidad), "cambio mínimo recursivo");
        igual(esperadoMin, ProgramacionDinamica.cambioMinimoMemoizado(monedas, cantidad), "cambio mínimo memoizado");
        igual(esperadoMin, ProgramacionDinamica.cambioMinimoTabla(monedas, cantidad), "cambio mínimo tabulado");
        igual(esperadoFormas, ProgramacionDinamica.cambioFormasRecursivo(monedas, cantidad), "formas recursivo");
        igual(esperadoFormas, ProgramacionDinamica.cambioFormasMemoizado(monedas, cantidad), "formas memoizado");
        igual(esperadoFormas, ProgramacionDinamica.cambioFormasTabla(monedas, cantidad), "formas tabulado");
    }

    private static void probarCambio() {
        verificarCambio(new int[0], 0, 0, 1);
        verificarCambio(new int[0], 5, -1, 0);
        verificarCambio(new int[]{1, 3, 4}, 6, 2, 4);
        verificarCambio(new int[]{4, 6}, 5, -1, 0);
        verificarCambio(new int[]{5, 1, 3, 3}, 6, 2, 4);

        Random rng = new Random(6025);
        for (int ensayo = 0; ensayo < 20; ensayo++) {
            int[] monedas = new int[rng.nextInt(5)];
            for (int i = 0; i < monedas.length; i++) monedas[i] = 1 + rng.nextInt(8);
            int[] unicas = Arrays.stream(monedas).distinct().sorted().toArray();
            int cantidad = rng.nextInt(16);
            verificarCambio(monedas, cantidad, cambioMinimoBfs(unicas, cantidad),
                    formasExhaustivas(unicas, 0, cantidad));
        }
        esperaError(() -> ProgramacionDinamica.cambioMinimoTabla(new int[]{0, 1}, 4), "denominación cero");
        System.out.println("OK cambio minimo y conteo de combinaciones");
    }

    private static boolean esSubsecuencia(int[] candidata, int[] texto) {
        int indice = 0;
        for (int simbolo : texto) {
            if (indice < candidata.length && candidata[indice] == simbolo) indice++;
        }
        return indice == candidata.length;
    }

    private static int lcsqExhaustiva(String a, String b) {
        int[] corto = a.codePointCount(0, a.length()) <= b.codePointCount(0, b.length())
                ? a.codePoints().toArray() : b.codePoints().toArray();
        int[] otro;
        if (a.codePointCount(0, a.length()) <= b.codePointCount(0, b.length())) otro = b.codePoints().toArray();
        else otro = a.codePoints().toArray();
        int mejor = 0;
        for (int mascara = 0; mascara < (1 << corto.length); mascara++) {
            int[] candidata = new int[Integer.bitCount(mascara)];
            int posicion = 0;
            for (int i = 0; i < corto.length; i++) {
                if ((mascara & (1 << i)) != 0) candidata[posicion++] = corto[i];
            }
            if (candidata.length > mejor && esSubsecuencia(candidata, otro)) mejor = candidata.length;
        }
        return mejor;
    }

    private static int subcadenaExhaustiva(String a, String b) {
        int[] aa = a.codePoints().toArray();
        int mejor = 0;
        for (int inicio = 0; inicio < aa.length; inicio++) {
            for (int fin = inicio + 1; fin <= aa.length; fin++) {
                String candidata = new String(aa, inicio, fin - inicio);
                int longitud = fin - inicio;
                if (longitud > mejor && b.contains(candidata)) mejor = longitud;
            }
        }
        return mejor;
    }

    private static void verificarLcs(String a, String b, int esperadoSubsecuencia, int esperadoSubcadena) {
        igual(esperadoSubsecuencia, ProgramacionDinamica.lcsSubsecuenciaRecursiva(a, b), "LCSq recursiva");
        igual(esperadoSubsecuencia, ProgramacionDinamica.lcsSubsecuenciaMemoizada(a, b), "LCSq memoizada");
        igual(esperadoSubsecuencia, ProgramacionDinamica.lcsSubsecuenciaTabla(a, b), "LCSq tabulada");
        igual(esperadoSubcadena, ProgramacionDinamica.lcsSubcadenaRecursiva(a, b), "LCS recursiva");
        igual(esperadoSubcadena, ProgramacionDinamica.lcsSubcadenaMemoizada(a, b), "LCS memoizada");
        igual(esperadoSubcadena, ProgramacionDinamica.lcsSubcadenaTabla(a, b), "LCS tabulada");
    }

    private static void probarSubsecuenciaYSubcadena() {
        verificarLcs("", "", 0, 0);
        verificarLcs("ABC", "", 0, 0);
        verificarLcs("ABC", "DEF", 0, 0);
        verificarLcs("ABCD", "XBDY", 2, 1);
        verificarLcs("XABYCDZ", "QABRCDS", 4, 2);
        verificarLcs("ABC", "ZABCZ", 3, 3);
        verificarLcs("😀x", "a😀x", 2, 2);

        Random rng = new Random(5230);
        for (int ensayo = 0; ensayo < 25; ensayo++) {
            String a = cadenaAzar(rng, rng.nextInt(9));
            String b = cadenaAzar(rng, rng.nextInt(9));
            verificarLcs(a, b, lcsqExhaustiva(a, b), subcadenaExhaustiva(a, b));
        }
        System.out.println("OK LCSq y LCS");
    }

    private static String cadenaAzar(Random rng, int n) {
        StringBuilder texto = new StringBuilder();
        for (int i = 0; i < n; i++) texto.append((char) ('A' + rng.nextInt(3)));
        return texto.toString();
    }

    public static void main(String[] args) {
        probarMochila();
        probarCambio();
        probarSubsecuenciaYSubcadena();
        System.out.println(verificaciones + " verificaciones Java correctas.");
    }
}

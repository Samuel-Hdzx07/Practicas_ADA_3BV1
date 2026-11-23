import java.util.Arrays;
import java.util.Locale;
import java.util.function.LongSupplier;

/** Mediciones simples en proceso; separan la carga común de las corridas escalables. */
public final class Benchmarks {
    private static volatile long sumidero;

    private Benchmarks() {}

    private static void medir(String problema, String estrategia, String carga,
                              int dimension, LongSupplier operacion) {
        sumidero = operacion.getAsLong(); // calentamiento de la JVM
        long[] nanosegundos = new long[3];
        long resultado = 0;
        for (int i = 0; i < nanosegundos.length; i++) {
            long inicio = System.nanoTime();
            resultado = operacion.getAsLong();
            nanosegundos[i] = System.nanoTime() - inicio;
            sumidero ^= resultado;
        }
        Arrays.sort(nanosegundos);
        double medianaMs = nanosegundos[1] / 1_000_000.0;
        System.out.printf(Locale.ROOT, "Java,%s,%s,%s,%d,%.6f,%d%n",
                problema, estrategia, carga, dimension, medianaMs, resultado);
    }

    private static int[] generar(int n, int multiplicador, int modulo, int incremento) {
        int[] datos = new int[n];
        for (int i = 0; i < n; i++) datos[i] = 1 + (i * multiplicador + incremento) % modulo;
        return datos;
    }

    private static String cadena(int n, int semilla) {
        StringBuilder texto = new StringBuilder(n);
        for (int i = 0; i < n; i++) texto.append((char) ('A' + ((i * 17 + semilla) % 4)));
        return texto.toString();
    }

    private static void medirGrupoPequeno() {
        int[] pesos = generar(18, 7, 17, 0);
        int[] valores = generar(18, 13, 50, 0);
        int capacidad = 55;
        medir("mochila", "recursion", "comun", 18,
                () -> ProgramacionDinamica.mochilaRecursiva(pesos, valores, capacidad));
        medir("mochila", "memoizacion", "comun", 18,
                () -> ProgramacionDinamica.mochilaMemoizada(pesos, valores, capacidad));
        medir("mochila", "tabulacion", "comun", 18,
                () -> ProgramacionDinamica.mochilaTabla(pesos, valores, capacidad));

        int[] monedas = {1, 3, 4, 7};
        medir("cambio_minimo", "recursion", "comun", 24,
                () -> ProgramacionDinamica.cambioMinimoRecursivo(monedas, 24));
        medir("cambio_minimo", "memoizacion", "comun", 24,
                () -> ProgramacionDinamica.cambioMinimoMemoizado(monedas, 24));
        medir("cambio_minimo", "tabulacion", "comun", 24,
                () -> ProgramacionDinamica.cambioMinimoTabla(monedas, 24));
        medir("cambio_formas", "recursion", "comun", 24,
                () -> ProgramacionDinamica.cambioFormasRecursivo(monedas, 24));
        medir("cambio_formas", "memoizacion", "comun", 24,
                () -> ProgramacionDinamica.cambioFormasMemoizado(monedas, 24));
        medir("cambio_formas", "tabulacion", "comun", 24,
                () -> ProgramacionDinamica.cambioFormasTabla(monedas, 24));

        String a = "AAAAAAAAAA", b = "BBBBBBBBBB";
        medir("LCSq", "recursion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubsecuenciaRecursiva(a, b));
        medir("LCSq", "memoizacion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubsecuenciaMemoizada(a, b));
        medir("LCSq", "tabulacion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubsecuenciaTabla(a, b));
        medir("LCS_subcadena", "recursion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubcadenaRecursiva(a, b));
        medir("LCS_subcadena", "memoizacion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubcadenaMemoizada(a, b));
        medir("LCS_subcadena", "tabulacion", "comun", a.length(),
                () -> ProgramacionDinamica.lcsSubcadenaTabla(a, b));
    }

    private static void medirGrupoEscalable() {
        int[] pesos = generar(90, 7, 19, 1);
        int[] valores = generar(90, 13, 47, 2);
        int capacidad = 700;
        medir("mochila", "memoizacion", "escalable", pesos.length,
                () -> ProgramacionDinamica.mochilaMemoizada(pesos, valores, capacidad));
        medir("mochila", "tabulacion", "escalable", pesos.length,
                () -> ProgramacionDinamica.mochilaTabla(pesos, valores, capacidad));

        int[] monedas = {7, 13, 29};
        medir("cambio_minimo", "memoizacion", "escalable", 600,
                () -> ProgramacionDinamica.cambioMinimoMemoizado(monedas, 600));
        medir("cambio_minimo", "tabulacion", "escalable", 600,
                () -> ProgramacionDinamica.cambioMinimoTabla(monedas, 600));
        medir("cambio_formas", "memoizacion", "escalable", 250,
                () -> ProgramacionDinamica.cambioFormasMemoizado(monedas, 250));
        medir("cambio_formas", "tabulacion", "escalable", 250,
                () -> ProgramacionDinamica.cambioFormasTabla(monedas, 250));

        String a = cadena(160, 1), b = cadena(160, 3);
        medir("LCSq", "memoizacion", "escalable", a.length(),
                () -> ProgramacionDinamica.lcsSubsecuenciaMemoizada(a, b));
        medir("LCSq", "tabulacion", "escalable", a.length(),
                () -> ProgramacionDinamica.lcsSubsecuenciaTabla(a, b));
        medir("LCS_subcadena", "memoizacion", "escalable", a.length(),
                () -> ProgramacionDinamica.lcsSubcadenaMemoizada(a, b));
        medir("LCS_subcadena", "tabulacion", "escalable", a.length(),
                () -> ProgramacionDinamica.lcsSubcadenaTabla(a, b));
    }

    public static void main(String[] args) {
        System.out.println("lenguaje,problema,estrategia,carga,dimension,mediana_ms,resultado");
        medirGrupoPequeno();
        medirGrupoEscalable();
    }
}

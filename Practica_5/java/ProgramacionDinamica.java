import java.util.Arrays;
import java.util.TreeSet;

/** Algoritmos de la práctica 5. Las cadenas se comparan por puntos de código Unicode. */
public final class ProgramacionDinamica {
    private ProgramacionDinamica() {}

    private static void validarMochila(int[] pesos, int[] valores, int capacidad) {
        if (pesos == null || valores == null || pesos.length != valores.length) {
            throw new IllegalArgumentException("pesos y valores deben tener la misma longitud");
        }
        if (capacidad < 0) throw new IllegalArgumentException("la capacidad no puede ser negativa");
        for (int peso : pesos) {
            if (peso <= 0) throw new IllegalArgumentException("los pesos deben ser enteros positivos");
        }
        for (int valor : valores) {
            if (valor < 0) throw new IllegalArgumentException("los valores no pueden ser negativos");
        }
    }

    public static int mochilaRecursiva(int[] pesos, int[] valores, int capacidad) {
        validarMochila(pesos, valores, capacidad);
        return mochilaRecursiva(pesos, valores, pesos.length, capacidad);
    }

    private static int mochilaRecursiva(int[] pesos, int[] valores, int n, int capacidad) {
        if (n == 0 || capacidad == 0) return 0;
        if (pesos[n - 1] > capacidad) return mochilaRecursiva(pesos, valores, n - 1, capacidad);
        return Math.max(
                mochilaRecursiva(pesos, valores, n - 1, capacidad),
                valores[n - 1] + mochilaRecursiva(pesos, valores, n - 1, capacidad - pesos[n - 1]));
    }

    public static int mochilaMemoizada(int[] pesos, int[] valores, int capacidad) {
        validarMochila(pesos, valores, capacidad);
        int[][] memo = new int[pesos.length + 1][capacidad + 1];
        for (int[] fila : memo) Arrays.fill(fila, -1);
        return mochilaMemoizada(pesos, valores, pesos.length, capacidad, memo);
    }

    private static int mochilaMemoizada(int[] pesos, int[] valores, int n, int capacidad, int[][] memo) {
        if (n == 0 || capacidad == 0) return 0;
        if (memo[n][capacidad] != -1) return memo[n][capacidad];
        if (pesos[n - 1] > capacidad) {
            memo[n][capacidad] = mochilaMemoizada(pesos, valores, n - 1, capacidad, memo);
        } else {
            memo[n][capacidad] = Math.max(
                    mochilaMemoizada(pesos, valores, n - 1, capacidad, memo),
                    valores[n - 1] + mochilaMemoizada(pesos, valores, n - 1,
                            capacidad - pesos[n - 1], memo));
        }
        return memo[n][capacidad];
    }

    public static int mochilaTabla(int[] pesos, int[] valores, int capacidad) {
        validarMochila(pesos, valores, capacidad);
        int[][] dp = new int[pesos.length + 1][capacidad + 1];
        for (int i = 1; i <= pesos.length; i++) {
            for (int c = 0; c <= capacidad; c++) {
                dp[i][c] = dp[i - 1][c];
                if (pesos[i - 1] <= c) {
                    dp[i][c] = Math.max(dp[i][c], valores[i - 1] + dp[i - 1][c - pesos[i - 1]]);
                }
            }
        }
        return dp[pesos.length][capacidad];
    }

    private static int[] normalizarMonedas(int[] monedas, int cantidad) {
        if (monedas == null) throw new IllegalArgumentException("las monedas no pueden ser null");
        if (cantidad < 0) throw new IllegalArgumentException("la cantidad no puede ser negativa");
        TreeSet<Integer> unicas = new TreeSet<>();
        for (int moneda : monedas) {
            if (moneda <= 0) throw new IllegalArgumentException("las denominaciones deben ser positivas");
            unicas.add(moneda);
        }
        return unicas.stream().mapToInt(Integer::intValue).toArray();
    }

    /** Devuelve -1 cuando la cantidad no se puede formar. */
    public static int cambioMinimoRecursivo(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        int infinito = cantidad + 1;
        int resultado = cambioMinimoRecursivo(coins, cantidad, infinito);
        return resultado == infinito ? -1 : resultado;
    }

    private static int cambioMinimoRecursivo(int[] coins, int restante, int infinito) {
        if (restante == 0) return 0;
        int mejor = infinito;
        for (int moneda : coins) {
            if (moneda > restante) break;
            int anterior = cambioMinimoRecursivo(coins, restante - moneda, infinito);
            if (anterior < infinito) mejor = Math.min(mejor, anterior + 1);
        }
        return mejor;
    }

    public static int cambioMinimoMemoizado(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        int[] memo = new int[cantidad + 1];
        Arrays.fill(memo, -2); // -2: no calculado; -1: imposible.
        memo[0] = 0;
        return cambioMinimoMemoizado(coins, cantidad, memo);
    }

    private static int cambioMinimoMemoizado(int[] coins, int restante, int[] memo) {
        if (memo[restante] != -2) return memo[restante];
        int mejor = Integer.MAX_VALUE;
        for (int moneda : coins) {
            if (moneda > restante) break;
            int anterior = cambioMinimoMemoizado(coins, restante - moneda, memo);
            if (anterior >= 0) mejor = Math.min(mejor, anterior + 1);
        }
        memo[restante] = mejor == Integer.MAX_VALUE ? -1 : mejor;
        return memo[restante];
    }

    public static int cambioMinimoTabla(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        int[] dp = new int[cantidad + 1];
        Arrays.fill(dp, cantidad + 1);
        dp[0] = 0;
        for (int total = 1; total <= cantidad; total++) {
            for (int moneda : coins) {
                if (moneda > total) break;
                if (dp[total - moneda] <= cantidad) dp[total] = Math.min(dp[total], dp[total - moneda] + 1);
            }
        }
        return dp[cantidad] > cantidad ? -1 : dp[cantidad];
    }

    /** Cuenta combinaciones sin distinguir el orden y permitiendo reutilizar monedas. */
    public static long cambioFormasRecursivo(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        return cambioFormasRecursivo(coins, 0, cantidad);
    }

    private static long cambioFormasRecursivo(int[] coins, int i, int restante) {
        if (restante == 0) return 1;
        if (restante < 0 || i == coins.length) return 0;
        return Math.addExact(cambioFormasRecursivo(coins, i + 1, restante),
                cambioFormasRecursivo(coins, i, restante - coins[i]));
    }

    public static long cambioFormasMemoizado(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        long[][] memo = new long[coins.length + 1][cantidad + 1];
        for (long[] fila : memo) Arrays.fill(fila, -1L);
        return cambioFormasMemoizado(coins, 0, cantidad, memo);
    }

    private static long cambioFormasMemoizado(int[] coins, int i, int restante, long[][] memo) {
        if (restante == 0) return 1;
        if (restante < 0 || i == coins.length) return 0;
        if (memo[i][restante] != -1L) return memo[i][restante];
        memo[i][restante] = Math.addExact(cambioFormasMemoizado(coins, i + 1, restante, memo),
                cambioFormasMemoizado(coins, i, restante - coins[i], memo));
        return memo[i][restante];
    }

    public static long cambioFormasTabla(int[] monedas, int cantidad) {
        int[] coins = normalizarMonedas(monedas, cantidad);
        long[] dp = new long[cantidad + 1];
        dp[0] = 1;
        for (int moneda : coins) {
            for (int total = moneda; total <= cantidad; total++) {
                dp[total] = Math.addExact(dp[total], dp[total - moneda]);
            }
        }
        return dp[cantidad];
    }

    public static int lcsSubsecuenciaRecursiva(String a, String b) {
        return lcsSubsecuenciaRecursiva(a.codePoints().toArray(), b.codePoints().toArray(), 0, 0);
    }

    private static int lcsSubsecuenciaRecursiva(int[] a, int[] b, int i, int j) {
        if (i == a.length || j == b.length) return 0;
        if (a[i] == b[j]) return 1 + lcsSubsecuenciaRecursiva(a, b, i + 1, j + 1);
        return Math.max(lcsSubsecuenciaRecursiva(a, b, i + 1, j),
                lcsSubsecuenciaRecursiva(a, b, i, j + 1));
    }

    public static int lcsSubsecuenciaMemoizada(String a, String b) {
        int[] aa = a.codePoints().toArray(), bb = b.codePoints().toArray();
        int[][] memo = new int[aa.length + 1][bb.length + 1];
        for (int[] fila : memo) Arrays.fill(fila, -1);
        return lcsSubsecuenciaMemoizada(aa, bb, 0, 0, memo);
    }

    private static int lcsSubsecuenciaMemoizada(int[] a, int[] b, int i, int j, int[][] memo) {
        if (i == a.length || j == b.length) return 0;
        if (memo[i][j] != -1) return memo[i][j];
        if (a[i] == b[j]) memo[i][j] = 1 + lcsSubsecuenciaMemoizada(a, b, i + 1, j + 1, memo);
        else memo[i][j] = Math.max(lcsSubsecuenciaMemoizada(a, b, i + 1, j, memo),
                lcsSubsecuenciaMemoizada(a, b, i, j + 1, memo));
        return memo[i][j];
    }

    public static int lcsSubsecuenciaTabla(String a, String b) {
        int[] aa = a.codePoints().toArray(), bb = b.codePoints().toArray();
        int[][] dp = new int[aa.length + 1][bb.length + 1];
        for (int i = 1; i <= aa.length; i++) {
            for (int j = 1; j <= bb.length; j++) {
                if (aa[i - 1] == bb[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
                else dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
        return dp[aa.length][bb.length];
    }

    public static int lcsSubcadenaRecursiva(String a, String b) {
        return lcsSubcadenaRecursiva(a.codePoints().toArray(), b.codePoints().toArray(), 0, 0);
    }

    private static int rachaRecursiva(int[] a, int[] b, int i, int j) {
        if (i == a.length || j == b.length || a[i] != b[j]) return 0;
        return 1 + rachaRecursiva(a, b, i + 1, j + 1);
    }

    private static int lcsSubcadenaRecursiva(int[] a, int[] b, int i, int j) {
        if (i == a.length || j == b.length) return 0;
        return Math.max(rachaRecursiva(a, b, i, j),
                Math.max(lcsSubcadenaRecursiva(a, b, i + 1, j),
                        lcsSubcadenaRecursiva(a, b, i, j + 1)));
    }

    public static int lcsSubcadenaMemoizada(String a, String b) {
        int[] aa = a.codePoints().toArray(), bb = b.codePoints().toArray();
        int[][] memoMejor = new int[aa.length + 1][bb.length + 1];
        int[][] memoRacha = new int[aa.length + 1][bb.length + 1];
        for (int[] fila : memoMejor) Arrays.fill(fila, -1);
        for (int[] fila : memoRacha) Arrays.fill(fila, -1);
        return lcsSubcadenaMemoizada(aa, bb, 0, 0, memoMejor, memoRacha);
    }

    private static int rachaMemoizada(int[] a, int[] b, int i, int j, int[][] memo) {
        if (i == a.length || j == b.length || a[i] != b[j]) return 0;
        if (memo[i][j] != -1) return memo[i][j];
        memo[i][j] = 1 + rachaMemoizada(a, b, i + 1, j + 1, memo);
        return memo[i][j];
    }

    private static int lcsSubcadenaMemoizada(int[] a, int[] b, int i, int j,
                                              int[][] memoMejor, int[][] memoRacha) {
        if (i == a.length || j == b.length) return 0;
        if (memoMejor[i][j] != -1) return memoMejor[i][j];
        memoMejor[i][j] = Math.max(rachaMemoizada(a, b, i, j, memoRacha),
                Math.max(lcsSubcadenaMemoizada(a, b, i + 1, j, memoMejor, memoRacha),
                        lcsSubcadenaMemoizada(a, b, i, j + 1, memoMejor, memoRacha)));
        return memoMejor[i][j];
    }

    public static int lcsSubcadenaTabla(String a, String b) {
        int[] aa = a.codePoints().toArray(), bb = b.codePoints().toArray();
        int[][] dp = new int[aa.length + 1][bb.length + 1];
        int mejor = 0;
        for (int i = 1; i <= aa.length; i++) {
            for (int j = 1; j <= bb.length; j++) {
                if (aa[i - 1] == bb[j - 1]) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                    mejor = Math.max(mejor, dp[i][j]);
                }
            }
        }
        return mejor;
    }
}

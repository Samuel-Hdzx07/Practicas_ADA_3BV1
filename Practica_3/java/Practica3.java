import java.io.*;
import java.util.*;

public class Practica3 {
    static final int M=10_000_000, UMBRAL=16;
    static class RNG {
        long x; RNG(long semilla){x=semilla;}
        long siguiente(){x=(1664525L*x+1013904223L)&0xffffffffL;return x;}
    }
    static int[] datos32(int n){
        int[] a=new int[n];for(int i=0;i<n;i++)a[i]=(int)((7654321L*i+1234567)%M+1);
        RNG r=new RNG(2026);for(int i=n-1;i>0;i--){int j=(int)(r.siguiente()%(i+1));int v=a[i];a[i]=a[j];a[j]=v;}return a;
    }
    static long[] datos64(int n){
        long[] a=new long[n];for(int i=0;i<n;i++)a[i]=(7654321L*i+1234567)%M+1;
        RNG r=new RNG(2026);for(int i=n-1;i>0;i--){int j=(int)(r.siguiente()%(i+1));long v=a[i];a[i]=a[j];a[j]=v;}return a;
    }
    static int quickselect(int[] a,int k){
        if(k<1||k>a.length)throw new IllegalArgumentException("k fuera de rango");
        int objetivo=k-1,izq=0,der=a.length-1;RNG r=new RNG(99);
        while(izq<=der){
            int pivote=a[izq+(int)(r.siguiente()%(der-izq+1))],menor=izq,i=izq,mayor=der;
            while(i<=mayor){
                if(a[i]<pivote){int v=a[i];a[i]=a[menor];a[menor]=v;menor++;i++;}
                else if(a[i]>pivote){int v=a[i];a[i]=a[mayor];a[mayor]=v;mayor--;}
                else i++;
            }
            if(objetivo<menor)der=menor-1;else if(objetivo>mayor)izq=mayor+1;else return pivote;
        }throw new AssertionError();
    }
    static long quickselect(long[] a,int k){
        if(k<1||k>a.length)throw new IllegalArgumentException("k fuera de rango");
        int objetivo=k-1,izq=0,der=a.length-1;RNG r=new RNG(99);
        while(izq<=der){
            long pivote=a[izq+(int)(r.siguiente()%(der-izq+1))];int menor=izq,i=izq,mayor=der;
            while(i<=mayor){
                if(a[i]<pivote){long v=a[i];a[i]=a[menor];a[menor]=v;menor++;i++;}
                else if(a[i]>pivote){long v=a[i];a[i]=a[mayor];a[mayor]=v;mayor--;}
                else i++;
            }
            if(objetivo<menor)der=menor-1;else if(objetivo>mayor)izq=mayor+1;else return pivote;
        }throw new AssertionError();
    }
    static long[] datos1d(int n,int semilla){long[] a=new long[n*n];RNG r=new RNG(semilla);for(int i=0;i<a.length;i++)a[i]=r.siguiente()%19-9;return a;}
    static long[][] datos2d(int n,int semilla){long[][] a=new long[n][n];RNG r=new RNG(semilla);for(int i=0;i<n;i++)for(int j=0;j<n;j++)a[i][j]=r.siguiente()%19-9;return a;}
    static long[] tradicional(long[] a,long[] b,int n){
        long[] c=new long[n*n];
        for(int i=0;i<n;i++)for(int k=0;k<n;k++){long v=a[i*n+k];for(int j=0;j<n;j++)c[i*n+j]+=v*b[k*n+j];}return c;
    }
    static long[][] tradicional(long[][] a,long[][] b,int n){
        long[][] c=new long[n][n];
        for(int i=0;i<n;i++)for(int k=0;k<n;k++){long v=a[i][k];for(int j=0;j<n;j++)c[i][j]+=v*b[k][j];}return c;
    }
    static long[] suma(long[] a,long[] b,int signo){long[] c=new long[a.length];for(int i=0;i<a.length;i++)c[i]=a[i]+signo*b[i];return c;}
    static long[][] suma(long[][] a,long[][] b,int signo){int n=a.length;long[][] c=new long[n][n];for(int i=0;i<n;i++)for(int j=0;j<n;j++)c[i][j]=a[i][j]+signo*b[i][j];return c;}
    static long[][] dividir(long[] a,int n){int h=n/2;long[][] p=new long[4][h*h];for(int q=0;q<4;q++)for(int i=0;i<h;i++)System.arraycopy(a,(i+(q/2)*h)*n+(q%2)*h,p[q],i*h,h);return p;}
    static long[][][] dividir(long[][] a,int n){int h=n/2;long[][][] p=new long[4][h][h];for(int q=0;q<4;q++)for(int i=0;i<h;i++)System.arraycopy(a[i+(q/2)*h],(q%2)*h,p[q][i],0,h);return p;}
    static long[] unir(long[] a,long[] b,long[] c,long[] d,int h){int n=2*h;long[] out=new long[n*n];for(int i=0;i<h;i++){System.arraycopy(a,i*h,out,i*n,h);System.arraycopy(b,i*h,out,i*n+h,h);System.arraycopy(c,i*h,out,(i+h)*n,h);System.arraycopy(d,i*h,out,(i+h)*n+h,h);}return out;}
    static long[][] unir(long[][] a,long[][] b,long[][] c,long[][] d,int h){int n=2*h;long[][] out=new long[n][n];for(int i=0;i<h;i++){System.arraycopy(a[i],0,out[i],0,h);System.arraycopy(b[i],0,out[i],h,h);System.arraycopy(c[i],0,out[i+h],0,h);System.arraycopy(d[i],0,out[i+h],h,h);}return out;}
    static long[] strassen(long[] a,long[] b,int n){return strassen(a,b,n,UMBRAL);}
    static long[] strassen(long[] a,long[] b,int n,int umbral){
        if(n<=umbral)return tradicional(a,b,n);int h=n/2;
        long[][] x=dividir(a,n),y=dividir(b,n);
        long[] m1=strassen(suma(x[0],x[3],1),suma(y[0],y[3],1),h,umbral);
        long[] m2=strassen(suma(x[2],x[3],1),y[0],h,umbral);
        long[] m3=strassen(x[0],suma(y[1],y[3],-1),h,umbral);
        long[] m4=strassen(x[3],suma(y[2],y[0],-1),h,umbral);
        long[] m5=strassen(suma(x[0],x[1],1),y[3],h,umbral);
        long[] m6=strassen(suma(x[2],x[0],-1),suma(y[0],y[1],1),h,umbral);
        long[] m7=strassen(suma(x[1],x[3],-1),suma(y[2],y[3],1),h,umbral);
        return unir(suma(suma(suma(m1,m4,1),m5,-1),m7,1),suma(m3,m5,1),suma(m2,m4,1),suma(suma(suma(m1,m2,-1),m3,1),m6,1),h);
    }
    static long[][] strassen(long[][] a,long[][] b,int n){return strassen(a,b,n,UMBRAL);}
    static long[][] strassen(long[][] a,long[][] b,int n,int umbral){
        if(n<=umbral)return tradicional(a,b,n);int h=n/2;
        long[][][] x=dividir(a,n),y=dividir(b,n);
        long[][] m1=strassen(suma(x[0],x[3],1),suma(y[0],y[3],1),h,umbral);
        long[][] m2=strassen(suma(x[2],x[3],1),y[0],h,umbral);
        long[][] m3=strassen(x[0],suma(y[1],y[3],-1),h,umbral);
        long[][] m4=strassen(x[3],suma(y[2],y[0],-1),h,umbral);
        long[][] m5=strassen(suma(x[0],x[1],1),y[3],h,umbral);
        long[][] m6=strassen(suma(x[2],x[0],-1),suma(y[0],y[1],1),h,umbral);
        long[][] m7=strassen(suma(x[1],x[3],-1),suma(y[2],y[3],1),h,umbral);
        return unir(suma(suma(suma(m1,m4,1),m5,-1),m7,1),suma(m3,m5,1),suma(m2,m4,1),suma(suma(suma(m1,m2,-1),m3,1),m6,1),h);
    }
    static long[] aplanar(long[][] a){int n=a.length;long[] c=new long[n*n];for(int i=0;i<n;i++)System.arraycopy(a[i],0,c,i*n,n);return c;}
    static void test(){
        int cuenta=0;
        for(int[] a:new int[][]{{9},{3,2,1},{2,2,1,2,3},{-5,0,4,-5}}){
            int[] ref=a.clone();Arrays.sort(ref);
            for(int k=1;k<=a.length;k++){if(quickselect(a.clone(),k)!=ref[k-1])throw new AssertionError();cuenta++;
                long[] largo=Arrays.stream(a).asLongStream().toArray();if(quickselect(largo,k)!=ref[k-1])throw new AssertionError();cuenta++;}
        }
        for(int n:new int[]{1,2,4,8,16,32}){
            long[][] a=datos2d(n,2026),b=datos2d(n,2027);long[] ref=new long[n*n];
            for(int i=0;i<n;i++)for(int j=0;j<n;j++)for(int k=0;k<n;k++)ref[i*n+j]+=a[i][k]*b[k][j];
            if(!Arrays.equals(tradicional(aplanar(a),aplanar(b),n),ref)||!Arrays.equals(aplanar(tradicional(a,b,n)),ref))throw new AssertionError();cuenta+=2;
            for(int corte:new int[]{1,16}){
                if(!Arrays.equals(strassen(aplanar(a),aplanar(b),n,corte),ref)||!Arrays.equals(aplanar(strassen(a,b,n,corte)),ref))throw new AssertionError();cuenta+=2;
            }
        }
        System.out.println(cuenta+" pruebas Java correctas");
    }
    public static void main(String[] args)throws Exception{
        if(args.length==0||args[0].equals("test")){test();return;}
        String tipo=args[0];int n=Integer.parseInt(args[1]);
        if(tipo.equals("reference")){
            long[] c=tradicional(datos1d(n,2026),datos1d(n,2027),n);
            try(DataOutputStream out=new DataOutputStream(new BufferedOutputStream(new FileOutputStream(args[2])))){for(long v:c)out.writeLong(v);}return;
        }
        if(tipo.equals("select")){
            int bits=Integer.parseInt(args[2]),k=(n+1)/2;quickselect(new int[]{3,1,2},2);
            long valor,inicio;double segundos;
            if(bits==32){int[] a=datos32(n);inicio=System.nanoTime();valor=quickselect(a,k);segundos=(System.nanoTime()-inicio)/1e9;}
            else{long[] a=datos64(n);inicio=System.nanoTime();valor=quickselect(a,k);segundos=(System.nanoTime()-inicio)/1e9;}
            int menores=0,iguales=0;for(int i=0;i<n;i++){long v=(7654321L*i+1234567)%M+1;if(v<valor)menores++;if(v==valor)iguales++;}
            boolean valido=menores<k&&k<=menores+iguales;
            System.out.println("{\"segundos\":"+segundos+",\"valido\":"+valido+",\"valor\":"+valor+",\"k\":"+k+"}");
        }else if(tipo.equals("matrix")){
            String metodo=args[2];boolean plana=args[3].equals("1d");long inicio;double segundos;long[] c;
            if(plana){long[] a=datos1d(n,2026),b=datos1d(n,2027);inicio=System.nanoTime();c=metodo.equals("strassen")?strassen(a,b,n):tradicional(a,b,n);segundos=(System.nanoTime()-inicio)/1e9;}
            else{long[][] a=datos2d(n,2026),b=datos2d(n,2027);inicio=System.nanoTime();long[][] z=metodo.equals("strassen")?strassen(a,b,n):tradicional(a,b,n);segundos=(System.nanoTime()-inicio)/1e9;c=aplanar(z);}
            boolean valido=true;
            try(DataInputStream in=new DataInputStream(new BufferedInputStream(new FileInputStream(args[4])))){for(long v:c)if(v!=in.readLong())valido=false;}
            System.out.println("{\"segundos\":"+segundos+",\"valido\":"+valido+"}");
        }else throw new IllegalArgumentException(tipo);
    }
}

public class Custom {
    public final boolean booleanField = true;
    public final byte byteField = 0x01;
    public final char charField = '\u0002';
    public final short shortField = 0x0123;
    public final int intField = 0x0123456;
    public final long longField = 0x0123456789L;
    public final float floatField = 123.456f;
    public final double doubleField = 123456.789789d;
    public final String stringField = "abcdef";

    public Custom() {}

    public static void staticVoidMethod() {}
    public static boolean staticBooleanMethod() { return false; }
    public static byte staticByteMethod() { return 0x32; }
    public static char staticCharMethod() { return '\u0196'; }
    public static short staticShortMethod() { return 0x1122; }
    public static int staticIntMethod() { return 0x00112233; }
    public static long staticLongMethod() { return 0x876543210L; }
    public static float staticFloatMethod() { return 98.6f; }
    public static double staticDoubleMethod() { return 777.665544d; }
    public static String staticStringMethod() { return "hello world"; }
}
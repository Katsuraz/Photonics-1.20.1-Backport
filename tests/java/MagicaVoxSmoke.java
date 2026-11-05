import at.redi2go.photonics.client.magicavoxel.InputBuffer;
import at.redi2go.photonics.client.magicavoxel.OutputBuffer;
import java.nio.ByteOrder;

public class MagicaVoxSmoke {
    public static void main(String[] args) {
        OutputBuffer output = new OutputBuffer(ByteOrder.LITTLE_ENDIAN);
        output.putInt(0x12345678);
        output.put((byte) 42);
        output.putInt(new int[]{2, 7, 13});
        InputBuffer input = new InputBuffer(ByteOrder.LITTLE_ENDIAN, output.array());
        require(input.getInt() == 0x12345678, "little-endian integer round trip");
        require(input.get() == (byte) 42, "byte round trip");
        int[] observed = new int[3];
        input.getInt(observed);
        require(observed[0] == 2 && observed[1] == 7 && observed[2] == 13, "integer array round trip");
        System.out.println("Java 17 Photonics 0.3.4 MagicaVox smoke test: PASS");
    }

    private static void require(boolean condition, String description) {
        if (!condition) throw new AssertionError(description);
    }
}

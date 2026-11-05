import at.redi2go.photonic.client.magicavoxel.MagicaVox;
import at.redi2go.photonic.client.magicavoxel.VoxReader;
import java.io.*;
import java.nio.charset.StandardCharsets;

/** Reconstructed VOX parser should run under a REAL Java 17 JVM. */
public final class LegacyVoxSmoke {
    private static void text(ByteArrayOutputStream stream, String value) throws IOException {
        stream.write(value.getBytes(StandardCharsets.UTF_8));
    }

    private static void le(ByteArrayOutputStream stream, int n) {
        for (int i = 0; i < 4; i++) stream.write((n >>> (i * 8)) & 255);
    }

    public static void main(String[] args) throws Exception {
        if (!System.getProperty("java.specification.version").equals("17")) {
            throw new AssertionError("Test must run on Java 17, not " + System.getProperty("java.version"));
        }
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        text(bytes, "VOX "); le(bytes, 150);
        text(bytes, "MAIN"); le(bytes, 0); le(bytes, 44);
        text(bytes, "SIZE"); le(bytes, 12); le(bytes, 0);
        le(bytes, 1); le(bytes, 1); le(bytes, 1);
        text(bytes, "XYZI"); le(bytes, 8); le(bytes, 0);
        le(bytes, 1); bytes.write(new byte[] { 0, 0, 0, 1 });

        MagicaVox.Vox vox = VoxReader.readToVox(new ByteArrayInputStream(bytes.toByteArray()));
        if (vox == null || vox.version != 150) throw new AssertionError("VOX header/version");
        MagicaVox.Size size = (MagicaVox.Size) vox.main.get(MagicaVox.Size.class).get(0).content;
        MagicaVox.Voxels voxels = (MagicaVox.Voxels) vox.main.get(MagicaVox.Voxels.class).get(0).content;
        if (size.width != 1 || size.height != 1 || size.depth != 1 ||
            voxels.get(0, 0, 0) != 1) {
            throw new AssertionError("Broken SIZE/XYZI deserialization");
        }
        System.out.println("PASS: rebuilt Photonics 0.2.5 VOX parser on Java 17");
    }
}

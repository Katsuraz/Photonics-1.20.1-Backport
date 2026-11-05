import at.redi2go.photonics.client.rendering.world.position.LightNodePos;
import at.redi2go.photonics.client.rendering.world.position.PBlockPos;
import at.redi2go.photonics.client.rendering.world.position.PChunkPos;

public class WorldPositionSmoke {
    public static void main(String[] args) {
        PBlockPos block = new PBlockPos(10, 20, 30);
        block.add(2, 3, 4);
        require(block.x == 12 && block.y == 23 && block.z == 34, "block add");
        block.sub(2, 3, 4);
        require(block.equals(new PBlockPos(10,20,30)), "block round trip");

        PChunkPos chunk = new PChunkPos(1, 2, 3);
        chunk.add(2, 3, 4);
        chunk.sub(2, 3, 4);
        require(chunk.equals(new PChunkPos(1,2,3)), "chunk add/sub round trip");

        LightNodePos light = new LightNodePos(10,20,30);
        light.add(2,3,4);
        light.sub(2,3,4);
        require(light.equals(new LightNodePos(10,20,30)), "light node add/sub round trip");
        System.out.println("Java 17 Photonics 0.3.4 world-position smoke test: PASS");
    }

    private static void require(boolean cond, String description) {
        if (!cond) throw new AssertionError(description);
    }
}

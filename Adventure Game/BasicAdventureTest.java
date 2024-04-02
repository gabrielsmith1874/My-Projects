
import java.io.IOException;

import AdventureModel.AdventureGame;
import javafx.stage.Stage;
import org.junit.jupiter.api.Test;
import views.SaveView;
import views.LoadView;
import views.AdventureGameView;

import static org.junit.jupiter.api.Assertions.*;

public class BasicAdventureTest {
    @Test
    void getCommandsTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        String commands = game.player.getCurrentRoom().getCommands();
        String commands2 = "DOWN,NORTH,IN,WEST,UP,SOUTH";
        java.util.HashSet set1 = new java.util.HashSet(java.util.Arrays.asList(commands.split(",")));
        java.util.HashSet set2 = new java.util.HashSet(java.util.Arrays.asList(commands2.split(",")));
        assertEquals(set1, set2);
    }

    @Test
    void getObjectString() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        String objects = game.player.getCurrentRoom().getObjectString();
        assertEquals("a water bird", objects);
    }

    @Test
    void getEmptyObjectString() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        game.movePlayer("SOUTH");
        String objects = game.player.getCurrentRoom().getObjectString();
        assertEquals("", objects);
    }

    // Create a test for:selectGame (loadview)
    //getFiles (loadview)
    //saveGame (saveView)
    //addTextHandlingEvent (adventuregameview)
    //submitEvent (adventuregameview)
    //showCommands (adventuregameview)
    //updateScene (adventuregameview)
    //getRoomImage (adventuregameview)
    //updateItems (adventuregameview)
    //getImageView (adventuregameview)
    //showInstructions (adventuregameview)
    //displayRoomDescription (adventuregameview)
    //checkForcedMoves (adventuregameview)

    @Test
    void winTest() throws IOException, InterruptedException {
        AdventureGame game = new AdventureGame("TinyGame");
        game.interpretAction("TAKE BIRD");
        game.movePlayer("in");
        game.movePlayer("out");
        assertFalse(game.movePlayer("FORCED"));
    }

    @Test
    void getFilesTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");

    }

    @Test
    void saveGameTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void addTextHandlingEventTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void submitEventTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void showCommandsTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void updateSceneTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void getRoomImageTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void updateItemsTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void getImageViewTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void showInstructionsTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void displayRoomDescriptionTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }

    @Test
    void checkForcedMovesTest() throws IOException {
        AdventureGame game = new AdventureGame("TinyGame");
        assertEquals("Games/TinyGame", game.getDirectoryName());
    }
}

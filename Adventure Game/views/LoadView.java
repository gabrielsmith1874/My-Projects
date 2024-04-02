package views;

import AdventureModel.AdventureGame;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.SelectionMode;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.*;


/**
 * Class LoadView.
 *
 * Loads Serialized adventure games.
 */
public class LoadView {

    private static AdventureGameView adventureGameView;
    private static Label selectGameLabel;
    private Button selectGameButton;
    private Button closeWindowButton;

    private static ListView<String> GameList;
    private String filename = null;
    /**
     * Constructor
     * @param adventureGameView the view
     */
    public LoadView(AdventureGameView adventureGameView){

        //note that the buttons in this view are not accessible!!
        this.adventureGameView = adventureGameView;
        selectGameLabel = new Label(String.format(""));

        GameList = new ListView<>(); //to hold all the file names

        final Stage dialog = new Stage(); //dialogue box
        dialog.initModality(Modality.APPLICATION_MODAL);
        dialog.initOwner(adventureGameView.stage);

        VBox dialogVbox = new VBox(20);
        dialogVbox.setPadding(new Insets(20, 20, 20, 20));
        dialogVbox.setStyle("-fx-background-color: #121212;");
        selectGameLabel.setId("CurrentGame"); // DO NOT MODIFY ID
        GameList.setId("GameList");  // DO NOT MODIFY ID
        GameList.getSelectionModel().setSelectionMode(SelectionMode.SINGLE);
        getFiles(GameList); //get files for file selector
        selectGameButton = new Button("Change Game");
        selectGameButton.setId("ChangeGame"); // DO NOT MODIFY ID
        AdventureGameView.makeButtonAccessible(selectGameButton, "select game", "This is the button to select a game", "Use this button to indicate a game file you would like to load.");

        closeWindowButton = new Button("Close Window");
        closeWindowButton.setId("closeWindowButton"); // DO NOT MODIFY ID
        closeWindowButton.setStyle("-fx-background-color: #17871b; -fx-text-fill: white;");
        closeWindowButton.setPrefSize(200, 50);
        closeWindowButton.setFont(new Font(16));
        closeWindowButton.setOnAction(e -> dialog.close());
        AdventureGameView.makeButtonAccessible(closeWindowButton, "close window", "This is a button to close the load game window", "Use this button to close the load game window.");

        //on selection, do something
        selectGameButton.setOnAction(e -> {
            try {
                selectGame(selectGameLabel, GameList);
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            }
        });

        VBox selectGameBox = new VBox(10, selectGameLabel, GameList, selectGameButton);

        // Default styles which can be modified
        GameList.setPrefHeight(100);
        selectGameLabel.setStyle("-fx-text-fill: #e8e6e3");
        selectGameLabel.setFont(new Font(16));
        selectGameButton.setStyle("-fx-background-color: #17871b; -fx-text-fill: white;");
        selectGameButton.setPrefSize(200, 50);
        selectGameButton.setFont(new Font(16));
        selectGameBox.setAlignment(Pos.CENTER);
        dialogVbox.getChildren().add(selectGameBox);
        Scene dialogScene = new Scene(dialogVbox, 400, 400);
        dialog.setScene(dialogScene);
        dialog.show();
    }

    /**
     * Get Files to display in the on screen ListView
     * Populate the listView attribute with .ser file names
     * Files will be located in the Games/Saved directory
     *
     * @param listView the ListView containing all the .ser files in the Games/Saved directory.
     */
    private void getFiles(ListView<String> listView) {
        // Define the directory where saved game files are located
        java.io.File dir = new java.io.File("Games/Saved");

        // List all files in the directory
        String[] files = dir.list();

        if (files != null) {
            // Iterate through the list of files
            for (String file : files) {
                // Check if the file has a ".ser" extension (serialized file)
                if (file.endsWith(".ser")) {
                    // Add the file name to the ListView
                    listView.getItems().add(file);
                }
            }
        }
    }

    /**
     * VoiceLoad
     * __________________________
     * Text will be a number in text (like one, two, three, etc.)
     * Convert text into an integer
     * If the integer is less than or equal to the number of files in the Games/Saved directory
     * Then select the file at that index
     * Call selectGame to load the game from the file
     * Otherwise, do nothing
     * @param text
     */
    public static void VoiceLoad(String text)
    {
        // convert text to integer
        int index = 0;
        switch (text) {
            case "one":
                index = 1;
                break;
            case "two":
                index = 2;
                break;
            case "three":
                index = 3;
                break;
            case "four":
                index = 4;
                break;
            case "five":
                index = 5;
                break;
            case "six":
                index = 6;
                break;
            case "seven":
                index = 7;
                break;
            case "eight":
                index = 8;
                break;
            case "nine":
                index = 9;
                break;
            case "ten":
                index = 10;
                break;
            default:
                break;
        }
        // if the integer is less than or equal to the number of files in the Games/Saved directory
        if (index <= GameList.getItems().size()) {
            // select the file at that index
            GameList.getSelectionModel().select(index - 1);
            // Call selectGame to load the game from the file
            try {
                selectGame(selectGameLabel, GameList);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Select the Game
     * Try to load a game from the Games/Saved
     * If successful, stop any articulation and put the name of the loaded file in the selectGameLabel.
     * If unsuccessful, stop any articulation and start an entirely new game from scratch.
     * In this case, change the selectGameLabel to indicate a new game has been loaded.
     *
     * @param selectGameLabel the label to use to print errors and or successes to the user.
     * @param GameList the ListView to populate
     */
    private static void selectGame(Label selectGameLabel, ListView<String> GameList) throws IOException {
        // Get the selected game from the list
        String selectedGame = GameList.getSelectionModel().getSelectedItem();

        // Construct the file path for the selected game
        String gameFile = "Games/Saved/" + selectedGame;

        if (selectedGame != null) {
            try {
                // Set the status label to indicate the loaded game
                selectGameLabel.setText("Game Loaded: " + selectedGame);

                // Stop any ongoing articulation of the game
                adventureGameView.stopArticulation();

                // Load the selected game model from the file
                adventureGameView.model = loadGame(gameFile);

                // Articulate the description of the current room
                adventureGameView.articulateRoomDescription();

                // Update the items in the game
                adventureGameView.updateItems();

                // Display the room description
                adventureGameView.displayRoomDescription();

                // Check forced moves
                adventureGameView.checkForcedMoves();
            } catch (Exception e) {
                // Create a new game if loading the game fails
                selectGameLabel.setText("Error Loading Game: " + selectedGame + ". \nStarting New Game.");

                // Stop any ongoing articulation of the game
                adventureGameView.stopArticulation();

                // Create a new AdventureGame model for a new game
                String[] gameList = adventureGameView.model.getDirectoryName().split("/");
                String gameName = gameList[gameList.length - 1];
                adventureGameView.model = new AdventureGame(gameName);
                AdventureGame game = adventureGameView.model;

                // Set up the new game
                game.setUpGame();

                // Articulate the description of the initial room
                adventureGameView.articulateRoomDescription();

                // Update the items in the game
                adventureGameView.updateItems();

                // Display the room description
                adventureGameView.displayRoomDescription();
            }
        }
    }

    /**
     * Load the Game from a file
     *
     * @param GameFile file to load
     * @return loaded Tetris Model
     * @throws IOException in the case of a file I/O error
     * @throws ClassNotFoundException in the case of a class not found error
     */
    public static AdventureGame loadGame(String GameFile) throws IOException, ClassNotFoundException {
        // Reading the object from a file
        FileInputStream file = null;
        ObjectInputStream in = null;
        try {
            file = new FileInputStream(GameFile);
            in = new ObjectInputStream(file);
            return (AdventureGame) in.readObject();
        } finally {
            if (in != null) {
                in.close();
                file.close();
            }
        }
    }

}

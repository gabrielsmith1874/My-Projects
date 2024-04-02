package views;

import AdventureModel.AdventureGame;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;
import java.util.Objects;

/**
 * Class SaveView.
 *
 * Saves Serialized adventure games.
 */
public class SaveView {

    static String saveFileSuccess = "Saved Adventure Game!!";
    static String saveFileExistsError = "Error: File already exists";
    static String saveFileNotSerError = "Error: File must end with .ser";
    private static Label saveFileErrorLabel = new Label("");
    private Label saveGameLabel = new Label(String.format("Enter name of file to save"));
    private static TextField saveFileNameTextField = new TextField("");
    private Button saveGameButton = new Button("Save Game");
    private Button closeWindowButton = new Button("Close Window");

    private static AdventureGameView adventureGameView;

    /**
     * Constructor
     * @param adventureGameView the view
     */
    public SaveView(AdventureGameView adventureGameView) {
        this.adventureGameView = adventureGameView;
        final Stage dialog = new Stage();
        dialog.initModality(Modality.APPLICATION_MODAL);
        dialog.initOwner(adventureGameView.stage);
        VBox dialogVbox = new VBox(20);
        dialogVbox.setPadding(new Insets(20, 20, 20, 20));
        dialogVbox.setStyle("-fx-background-color: #121212;");
        saveGameLabel.setId("SaveGame"); // DO NOT MODIFY ID
        saveFileErrorLabel.setId("SaveFileErrorLabel");
        saveFileNameTextField.setId("SaveFileNameTextField");
        saveGameLabel.setStyle("-fx-text-fill: #e8e6e3;");
        saveGameLabel.setFont(new Font(16));
        saveFileErrorLabel.setStyle("-fx-text-fill: #e8e6e3;");
        saveFileErrorLabel.setFont(new Font(16));
        saveFileNameTextField.setStyle("-fx-text-fill: #000000;");
        saveFileNameTextField.setFont(new Font(16));

        String gameName = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss").format(new Date()) + ".ser";
        saveFileNameTextField.setText(gameName);

        saveGameButton = new Button("Save board");
        saveGameButton.setId("SaveBoardButton"); // DO NOT MODIFY ID
        saveGameButton.setStyle("-fx-background-color: #17871b; -fx-text-fill: white;");
        saveGameButton.setPrefSize(200, 50);
        saveGameButton.setFont(new Font(16));
        AdventureGameView.makeButtonAccessible(saveGameButton, "save game", "This is a button to save the game", "Use this button to save the current game.");
        saveGameButton.setOnAction(e -> saveGame());

        closeWindowButton = new Button("Close Window");
        closeWindowButton.setId("closeWindowButton"); // DO NOT MODIFY ID
        closeWindowButton.setStyle("-fx-background-color: #17871b; -fx-text-fill: white;");
        closeWindowButton.setPrefSize(200, 50);
        closeWindowButton.setFont(new Font(16));
        closeWindowButton.setOnAction(e -> dialog.close());
        AdventureGameView.makeButtonAccessible(closeWindowButton, "close window", "This is a button to close the save game window", "Use this button to close the save game window.");

        VBox saveGameBox = new VBox(10, saveGameLabel, saveFileNameTextField, saveGameButton, saveFileErrorLabel, closeWindowButton);
        saveGameBox.setAlignment(Pos.CENTER);

        dialogVbox.getChildren().add(saveGameBox);
        Scene dialogScene = new Scene(dialogVbox, 400, 400);
        dialog.setScene(dialogScene);
        dialog.show();
    }

    /**
     * Convert index into an integer (index will be one, two, three, etc.)
     * Loop through files in the directory
     * If the file index matches the index, delete the file
     * Replace the file at the index with the current game
     *
     * @param index
     */
    public static void VoiceSave(String index) {
        //convert index to integer one = 1, two = 2, etc.
        int indexInt = convertStringToInteger(index);

        // Specify the folder path and file name
        String folderPath = "Games/Saved/";

        // Create a File object for the folder
        java.io.File folder = new java.io.File(folderPath);

        // Loop through saves
        int count = 0;
        for (java.io.File file : Objects.requireNonNull(folder.listFiles())) {
            if (file.isFile()) {
                if (count == indexInt) {
                    saveFileNameTextField.setText(file.getName());
                    saveGame();
                }
            }
            count++;
        }

    }

    /**
        * Convert a strings (one, two, three, ...) to an integer (1-20)
        * @param numberString the string to convert
        * @return the integer
     */
    public static int convertStringToInteger(String numberString) {
        int number = 0;
        switch (numberString) {
            case "one":
                number = 1;
                break;
            case "two":
                number = 2;
                break;
            case "three":
                number = 3;
                break;
            case "four":
                number = 4;
                break;
            case "five":
                number = 5;
                break;
            case "six":
                number = 6;
                break;
            case "seven":
                number = 7;
                break;
            case "eight":
                number = 8;
                break;
            case "nine":
                number = 9;
                break;
            case "ten":
                number = 10;
                break;
            case "eleven":
                number = 11;
                break;
            case "twelve":
                number = 12;
                break;
            case "thirteen":
                number = 13;
                break;
            case "fourteen":
                number = 14;
                break;
            case "fifteen":
                number = 15;
                break;
            case "sixteen":
                number = 16;
                break;
            case "seventeen":
                number = 17;
                break;
            case "eighteen":
                number = 18;
                break;
            case "nineteen":
                number = 19;
                break;
            case "twenty":
                number = 20;
                break;
            default:
        }
        return number;
    }

    /**
     * Saves the Game
     * Save the game to a serialized (binary) file.
     * Get the name of the file from saveFileNameTextField.
     * Files will be saved to the Games/Saved directory.
     * If the file already exists, set the saveFileErrorLabel to the text in saveFileExistsError
     * If the file doesn't end in .ser, set the saveFileErrorLabel to the text in saveFileNotSerError
     * Otherwise, load the file and set the saveFileErrorLabel to the text in saveFileSuccess
     */
    private static void saveGame() {
        // Specify the folder path and file name
        String folderPath = "Games/Saved/";

        // Create a File object for the folder
        java.io.File folder = new java.io.File(folderPath);

        boolean mkdir = folder.mkdir();

        // Get the file name from the text field
        String fileName = saveFileNameTextField.getText();

        // Check if the file name ends with .ser
        if (!fileName.endsWith(".ser")) {
            // Set the error label to the text in saveFileNotSerError
            saveFileErrorLabel.setText(saveFileNotSerError);
        }
        else
        {
            // Create a File object for the file
            java.io.File file = new java.io.File(folderPath + fileName);

            try
            {
                if(file.createNewFile())
                {
                    // Save the adventure game class to a file
                    AdventureGame adventureGame = adventureGameView.model;
                    adventureGame.saveModel(file);
                    saveFileErrorLabel.setText(saveFileSuccess);
                }
                else
                {
                    // Set the error label to the text in saveFileExistsError
                    saveFileErrorLabel.setText(saveFileExistsError);
                }
            }
            catch (Exception e)
            {
                // Set the error label to the text in saveFileExistsError
                saveFileErrorLabel.setText(saveFileExistsError);
            }
        }
    }


}


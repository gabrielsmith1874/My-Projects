package views;

import AdventureModel.AdventureGame;
import AdventureModel.AdventureObject;
import views.LoadView;
import views.SaveView;
import AdventureModel.Passage;
import javafx.animation.PauseTransition;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.scene.paint.Color;
import javafx.scene.layout.*;
import javafx.scene.input.KeyEvent; //you will need these!
import javafx.scene.input.KeyCode;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.util.Duration;
import javafx.event.EventHandler; //you will need this too!
import javafx.scene.AccessibleRole;
import VoiceRecognition.VoiceRecognition;

import java.io.File;
import java.util.List;

/**
 * Class AdventureGameView.
 *
 * This is the Class that will visualize your model.
 * You are asked to demo your visualization via a Zoom
 * recording. Place a link to your recording below.
 *
 * ZOOM LINK: https://drive.google.com/file/d/1lwiTCqDcCfEW0GaWo1xnm7SZniUmLL_l/view?usp=sharing
 * PASSWORD: N/A
 */
public class AdventureGameView {

    static AdventureGame model; //model of the game
    Stage stage; //stage on which all is rendered
    Button saveButton, loadButton, helpButton; //buttons
    Boolean helpToggle = false; //is help on display?

    Boolean save = false;
    Boolean load = false;

    GridPane gridPane = new GridPane(); //to hold images and buttons
    Label roomDescLabel = new Label(); //to hold room description and/or instructions
    VBox objectsInRoom = new VBox(); //to hold room items
    VBox objectsInInventory = new VBox(); //to hold inventory items
    ImageView roomImageView; //to hold room image
    TextField inputTextField; //for user input
    VoiceRecognition speechRecognition = new VoiceRecognition();
    private MediaPlayer mediaPlayer; //to play audio
    private boolean mediaPlaying; //to know if the audio is playing

    /**
     * Adventure Game View Constructor
     * __________________________
     * Initializes attributes
     * @param model the model of the game
     * @param stage the stage on which the game is rendered
     */
    public AdventureGameView(AdventureGame model, Stage stage) {
        this.model = model;
        this.stage = stage;
        intiUI();
    }

    /**
     * Initialize the UI
     */
    public void intiUI() {

        // setting up the stage
        this.stage.setTitle("smithg38's Adventure Game"); //Replace <YOUR UTORID> with your UtorID

        //Inventory + Room items
        objectsInInventory.setSpacing(10);
        objectsInInventory.setAlignment(Pos.TOP_CENTER);
        objectsInRoom.setSpacing(10);
        objectsInRoom.setAlignment(Pos.TOP_CENTER);

        // GridPane, anyone?
        gridPane.setPadding(new Insets(20));
        gridPane.setBackground(new Background(new BackgroundFill(
                Color.valueOf("#000000"),
                new CornerRadii(0),
                new Insets(0)
        )));

        //Three columns, three rows for the GridPane
        ColumnConstraints column1 = new ColumnConstraints(150);
        ColumnConstraints column2 = new ColumnConstraints(650);
        ColumnConstraints column3 = new ColumnConstraints(150);
        column3.setHgrow( Priority.SOMETIMES ); //let some columns grow to take any extra space
        column1.setHgrow( Priority.SOMETIMES );

        // Row constraints
        RowConstraints row1 = new RowConstraints();
        RowConstraints row2 = new RowConstraints( 550 );
        RowConstraints row3 = new RowConstraints();
        row1.setVgrow( Priority.SOMETIMES );
        row3.setVgrow( Priority.SOMETIMES );

        gridPane.getColumnConstraints().addAll( column1 , column2 , column1 );
        gridPane.getRowConstraints().addAll( row1 , row2 , row1 );

        // Buttons
        saveButton = new Button("Save");
        saveButton.setId("Save");
        customizeButton(saveButton, 100, 50);
        makeButtonAccessible(saveButton, "Save Button", "This button saves the game.", "This button saves the game. Click it in order to save your current progress, so you can play more later.");
        addSaveEvent();

        loadButton = new Button("Load");
        loadButton.setId("Load");
        customizeButton(loadButton, 100, 50);
        makeButtonAccessible(loadButton, "Load Button", "This button loads a game from a file.", "This button loads the game from a file. Click it in order to load a game that you saved at a prior date.");
        addLoadEvent();

        helpButton = new Button("Instructions");
        helpButton.setId("Instructions");
        customizeButton(helpButton, 200, 50);
        makeButtonAccessible(helpButton, "Help Button", "This button gives game instructions.", "This button gives instructions on the game controls. Click it to learn how to play.");
        addInstructionEvent();

        HBox topButtons = new HBox();
        topButtons.getChildren().addAll(saveButton, helpButton, loadButton);
        topButtons.setSpacing(10);
        topButtons.setAlignment(Pos.CENTER);

        inputTextField = new TextField();
        inputTextField.setFont(new Font("Arial", 16));
        inputTextField.setFocusTraversable(true);

        inputTextField.setAccessibleRole(AccessibleRole.TEXT_AREA);
        inputTextField.setAccessibleRoleDescription("Text Entry Box");
        inputTextField.setAccessibleText("Enter commands in this box.");
        inputTextField.setAccessibleHelp("This is the area in which you can enter commands you would like to play.  Enter a command and hit return to continue.");
        addTextHandlingEvent(); //attach an event to this input field

        //labels for inventory and room items
        Label objLabel =  new Label("Objects in Room");
        objLabel.setAlignment(Pos.CENTER);
        objLabel.setStyle("-fx-text-fill: white;");
        objLabel.setFont(new Font("Arial", 16));

        Label invLabel =  new Label("Your Inventory");
        invLabel.setAlignment(Pos.CENTER);
        invLabel.setStyle("-fx-text-fill: white;");
        invLabel.setFont(new Font("Arial", 16));

        //add all the widgets to the GridPane
        gridPane.add( objLabel, 0, 0, 1, 1 );  // Add label
        gridPane.add( topButtons, 1, 0, 1, 1 );  // Add buttons
        gridPane.add( invLabel, 2, 0, 1, 1 );  // Add label

        Label commandLabel = new Label("What would you like to do?");
        commandLabel.setStyle("-fx-text-fill: white;");
        commandLabel.setFont(new Font("Arial", 16));

        updateScene(""); //method displays an image and whatever text is supplied
        updateItems(); //update items shows inventory and objects in rooms

        // adding the text area and submit button to a VBox
        VBox textEntry = new VBox();
        textEntry.setStyle("-fx-background-color: #000000;");
        textEntry.setPadding(new Insets(20, 20, 20, 20));
        textEntry.getChildren().addAll(commandLabel, inputTextField);
        textEntry.setSpacing(10);
        textEntry.setAlignment(Pos.CENTER);
        gridPane.add( textEntry, 0, 2, 3, 1 );

        // Render everything
        var scene = new Scene( gridPane ,  1000, 800);
        scene.setFill(Color.BLACK);
        this.stage.setScene(scene);
        this.stage.setResizable(false);
        this.stage.show();

        speechRecognition.startSpeechRecognition(model, this);

    }


    /**
     * makeButtonAccessible
     * __________________________
     * For information about ARIA standards, see
     * https://www.w3.org/WAI/standards-guidelines/aria/
     *
     * @param inputButton the button to add screenreader hooks to
     * @param name ARIA name
     * @param shortString ARIA accessible text
     * @param longString ARIA accessible help text
     */
    public static void makeButtonAccessible(Button inputButton, String name, String shortString, String longString) {
        inputButton.setAccessibleRole(AccessibleRole.BUTTON);
        inputButton.setAccessibleRoleDescription(name);
        inputButton.setAccessibleText(shortString);
        inputButton.setAccessibleHelp(longString);
        inputButton.setFocusTraversable(true);
    }

    /**
     * customizeButton
     * __________________________
     *
     * @param inputButton the button to make stylish :)
     * @param w width
     * @param h height
     */
    private void customizeButton(Button inputButton, int w, int h) {
        inputButton.setPrefSize(w, h);
        inputButton.setFont(new Font("Arial", 16));
        inputButton.setStyle("-fx-background-color: #17871b; -fx-text-fill: white;");
    }

    /**
     * addTextHandlingEvent
     * __________________________
     * Add an event handler to the myTextField attribute
     *
     * Your event handler should respond when users
     * hits the ENTER or TAB KEY. If the user hits
     * the ENTER Key, strip white space from the
     * input to myTextField and pass the stripped
     * string to submitEvent for processing.
     *
     * If the user hits the TAB key, move the focus
     * of the scene onto any other node in the scene
     * graph by invoking requestFocus method.
     */
    private void addTextHandlingEvent() {
        inputTextField.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent event) {
                if (event.getCode() == KeyCode.ENTER){
                    submitEvent(inputTextField.getText().strip());
                    inputTextField.setText("");
                }
                else if (event.getCode() == KeyCode.TAB){
                    gridPane.requestFocus();
                }
            }
        });
    }

    public void processVoiceCommand(String command) {
        command = command.toLowerCase().strip();
        if (save) {
            save = false;
            //check if command is number (one, two, three, etc.)
            if (command.equalsIgnoreCase("one") || command.equalsIgnoreCase("two") || command.equalsIgnoreCase("three") || command.equalsIgnoreCase("four") || command.equalsIgnoreCase("five") || command.equalsIgnoreCase("six") || command.equalsIgnoreCase("seven") || command.equalsIgnoreCase("eight") || command.equalsIgnoreCase("nine") || command.equalsIgnoreCase("ten") || command.equalsIgnoreCase("eleven") || command.equalsIgnoreCase("twelve") || command.equalsIgnoreCase("thirteen") || command.equalsIgnoreCase("fourteen") || command.equalsIgnoreCase("fifteen") || command.equalsIgnoreCase("sixteen") || command.equalsIgnoreCase("seventeen") || command.equalsIgnoreCase("eighteen") || command.equalsIgnoreCase("nineteen") || command.equalsIgnoreCase("twenty")) {
                SaveView.VoiceSave(command);
            }
            else {
                updateScene("Give a save slot between 1 and 20.");
            }

        }
        else if (load) {
            load = false;
            //check if command is number (one, two, three, etc.)
            if (command.equalsIgnoreCase("one") || command.equalsIgnoreCase("two") || command.equalsIgnoreCase("three") || command.equalsIgnoreCase("four") || command.equalsIgnoreCase("five") || command.equalsIgnoreCase("six") || command.equalsIgnoreCase("seven") || command.equalsIgnoreCase("eight") || command.equalsIgnoreCase("nine") || command.equalsIgnoreCase("ten") || command.equalsIgnoreCase("eleven") || command.equalsIgnoreCase("twelve") || command.equalsIgnoreCase("thirteen") || command.equalsIgnoreCase("fourteen") || command.equalsIgnoreCase("fifteen") || command.equalsIgnoreCase("sixteen") || command.equalsIgnoreCase("seventeen") || command.equalsIgnoreCase("eighteen") || command.equalsIgnoreCase("nineteen") || command.equalsIgnoreCase("twenty")) {
                LoadView.VoiceLoad(command);
            }
            else {
                updateScene("Give a load slot between 1 and 20.");
            }
        }
        else if (checkvalid(command)) {
            command = command.toUpperCase();
            submitEvent(command);
        }
    }

    /**
     * submitEvent
     * __________________________
     *
     * @param text the command that needs to be processed
     */
    private void submitEvent(String text) {

        text = text.strip(); //get rid of white space
        stopArticulation(); //if speaking, stop

        if (text.equalsIgnoreCase("LOOK") || text.equalsIgnoreCase("L")) {
            Platform.runLater(new Runnable() {
                AdventureGame model = AdventureGameView.this.model;
                @Override
                public void run() {
                    Platform.setImplicitExit(false);
                    String roomDesc = this.model.getPlayer().getCurrentRoom().getRoomDescription();
                    String objectString = this.model.getPlayer().getCurrentRoom().getObjectString();
                    if (!objectString.isEmpty())
                        roomDescLabel.setText(roomDesc + "\n\nObjects in this room:\n" + objectString);
                    articulateRoomDescription(); //all we want, if we are looking, is to repeat description.
                }
            });
            return;
        } else if (text.equalsIgnoreCase("HELP") || text.equalsIgnoreCase("H")) {
            showInstructions();
            return;
        } else if (text.equalsIgnoreCase("COMMANDS") || text.equalsIgnoreCase("C")) {
            showCommands(); //this is new!  We did not have this command in A1
            return;
        }


        //try to move!
        String output = this.model.interpretAction(text); //process the command!


        // forced
        if (output == null || (!output.equals("GAME OVER") && !output.equals("FORCED") && !output.equals("HELP"))) {
            updateScene(output);
            updateItems();
        } else if (output.equals("GAME OVER")) {
            updateScene("");
            updateItems();
            PauseTransition pause = new PauseTransition(Duration.seconds(10));
            pause.setOnFinished(event -> {
                Platform.exit();
            });
            pause.play();
        }
        else if (output.equals("FORCED"))
        {
            //forced move that is not game over
            articulateRoomDescription();
            updateItems();
            displayRoomDescription();
            // after pause, move player to forced room and update scene
            PauseTransition pause = new PauseTransition(Duration.seconds(5));
            pause.setOnFinished(event -> {
                articulateRoomDescription();
                updateItems();
                displayRoomDescription();
                submitEvent("FORCED");
            });
            pause.play();
        }
    }
    private boolean checkvalid(String text) {
        if (text.equalsIgnoreCase("UP") || text.equalsIgnoreCase("U") || text.equalsIgnoreCase("DOWN") || text.equalsIgnoreCase("D") || text.equalsIgnoreCase("NORTH") || text.equalsIgnoreCase("N") || text.equalsIgnoreCase("SOUTH") || text.equalsIgnoreCase("S") || text.equalsIgnoreCase("EAST") || text.equalsIgnoreCase("E") || text.equalsIgnoreCase("WEST") || text.equalsIgnoreCase("W") || text.equalsIgnoreCase("IN") || text.equalsIgnoreCase("I") || text.equalsIgnoreCase("OUT") || text.equalsIgnoreCase("O")) {
            List<Passage> directions = this.model.getPlayer().getCurrentRoom().getMotionTable().getDirection();
            for (int i = 0; i < directions.size(); i++) {
                if (text.equalsIgnoreCase(directions.get(i).getDirection())) {
                    return true;
                }
            }
            updateScene("You can't go that way.");
            return false;
        }
        if (text.contains("TAKE") || text.contains("T") || text.contains("DROP") || text.contains("D") || text.equalsIgnoreCase("INVENTORY") || text.equalsIgnoreCase("I")) {
            return true;
        }
        if (text.equalsIgnoreCase("QUIT") || text.equalsIgnoreCase("Q")) {
            Platform.exit();
        }
        if (text.equalsIgnoreCase("LOOK") || text.equalsIgnoreCase("L") || text.equalsIgnoreCase("HELP") || text.equalsIgnoreCase("H") || text.equalsIgnoreCase("COMMANDS") || text.equalsIgnoreCase("C")) {
            return true;
        }
        if (text.equalsIgnoreCase("SAVE") || text.equalsIgnoreCase("LOAD") ) {
            updateScene("Which game would you like to " + text.toLowerCase() + "?");
            save = text.equalsIgnoreCase("SAVE");
            load = text.equalsIgnoreCase("LOAD");
            return false;
        }
        //inventory
        updateScene("I don't understand that command.");
        return false;
    }

    /**
     * showCommands
     * __________________________
     *
     * update the text in the GUI (within roomDescLabel)
     * to show all the moves that are possible from the
     * current room.
     */
    private void showCommands() {
        // Initialize a string to store the available commands
        String output = "You can move in the following directions:\n";

        // Get the list of available directions from the current room's motion table
        List<Passage> directions = this.model.getPlayer().getCurrentRoom().getMotionTable().getDirection();

        // Iterate through the list of directions
        for (int i = 0; i < directions.size(); i++) {
            // Append each direction to the output string
            output += directions.get(i).getDirection() + "\n";
        }

        // Update the user interface to display the available commands
        roomDescLabel.setText(output);
    }


    /**
     * updateScene
     * __________________________
     *
     * Show the current room, and print some text below it.
     * If the input parameter is not null, it will be displayed
     * below the image.
     * Otherwise, the current room description will be displayed
     * below the image.
     *
     * @param textToDisplay the text to display below the image.
     */
    public void updateScene(String textToDisplay) {
        Platform.runLater(new Runnable() {
            @Override
            public void run() {
                Platform.setImplicitExit(false);
                // Get the image of the current room
                getRoomImage();

                // Format the text to display
                formatText(textToDisplay);

                // Set the preferred width and height for the room description label
                roomDescLabel.setPrefWidth(500);
                roomDescLabel.setPrefHeight(500);

                // Clip the text if it overflows the label
                roomDescLabel.setTextOverrun(OverrunStyle.CLIP);

                // Enable text wrapping within the label
                roomDescLabel.setWrapText(true);

                // Create a VBox containing the room image and description label
                VBox roomPane = new VBox(roomImageView, roomDescLabel);

                // Set padding and alignment for the VBox
                roomPane.setPadding(new Insets(10));
                roomPane.setAlignment(Pos.TOP_CENTER);

                // Set the background color of the roomPane
                roomPane.setStyle("-fx-background-color: #000000;");

                // Add the roomPane to the gridPane at position (1, 1)
                gridPane.add(roomPane, 1, 1);

                // Adjust the stage size to fit the updated scene
                stage.sizeToScene();

                // Finally, articulate the room description if it's provided
                if (textToDisplay == null || textToDisplay.isBlank()) {
                    stopArticulation();
                    articulateRoomDescription();
                }
            }
        });
    }

    /**
     * formatText
     * __________________________
     *
     * Format text for display.
     *
     * @param textToDisplay the text to be formatted for display.
     */
    private void formatText(String textToDisplay) {
        if (textToDisplay == null || textToDisplay.isBlank()) {
            String roomDesc = this.model.getPlayer().getCurrentRoom().getRoomDescription() + "\n";
            String objectString = this.model.getPlayer().getCurrentRoom().getObjectString();
            if (objectString != null && !objectString.isEmpty()) roomDescLabel.setText(roomDesc + "\n\nObjects in this room:\n" + objectString);
            else roomDescLabel.setText(roomDesc);
        } else roomDescLabel.setText(textToDisplay);
        roomDescLabel.setStyle("-fx-text-fill: white;");
        roomDescLabel.setFont(new Font("Arial", 16));
        roomDescLabel.setAlignment(Pos.CENTER);
    }

    /**
     * getRoomImage
     * __________________________
     *
     * Get the image for the current room and place
     * it in the roomImageView
     */
    private void getRoomImage() {
        Platform.setImplicitExit(false);
        int roomNumber = this.model.getPlayer().getCurrentRoom().getRoomNumber();
        String roomImage = this.model.getDirectoryName() + "/room-images/" + roomNumber + ".png";

        Image roomImageFile = new Image(roomImage);
        roomImageView = new ImageView(roomImageFile);
        roomImageView.setPreserveRatio(true);
        roomImageView.setFitWidth(400);
        roomImageView.setFitHeight(400);

        //set accessible text
        roomImageView.setAccessibleRole(AccessibleRole.IMAGE_VIEW);
        roomImageView.setAccessibleText(this.model.getPlayer().getCurrentRoom().getRoomDescription());
        roomImageView.setFocusTraversable(true);
    }

    /**
     * updateItems
     * __________________________
     *
     * This method is partially completed, but you are asked to finish it off.
     *
     * The method should populate the objectsInRoom and objectsInInventory Vboxes.
     * Each Vbox should contain a collection of nodes (Buttons, ImageViews, you can decide)
     * Each node represents a different object.
     *
     * Images of each object are in the assets
     * folders of the given adventure game.
     */
    public void updateItems() {

        Platform.runLater(new Runnable() {

            private AdventureGame model = AdventureGameView.this.model;

            @Override
            public void run() {
                Platform.setImplicitExit(false);
                //write some code here to add images of objects in a given room to the objectsInRoom Vbox
                //write some code here to add images of objects in a player's inventory room to the objectsInInventory Vbox
                //please use setAccessibleText to add "alt" descriptions to your images!
                //the path to the image of any is as follows:
                //this.model.getDirectoryName() + "/objectImages/" + objectName + ".jpg";

                // Clear the UI elements displaying objects in the current room and the player's inventory
                objectsInRoom.getChildren().clear();
                objectsInInventory.getChildren().clear();

                // Iterate through objects in the current room and create ImageView elements for each
                for (int i = 0; i < this.model.getPlayer().getCurrentRoom().objectsInRoom.size(); i++) {
                    AdventureObject object = this.model.getPlayer().getCurrentRoom().objectsInRoom.get(i);
                    ImageView objectImageView = getImageView(i, false);
                    Button objectButton = new Button("", objectImageView);
                    makeButtonAccessible(objectButton, object.getName(), object.getDescription(), object.getDescription() + ". Click on the image to take the object.");
                    VBox vbox = new VBox(objectImageView, new Text(object.getName()));
                    vbox.setAlignment(Pos.CENTER);
                    objectButton.setGraphic(vbox);
                    objectButton.setOnAction(e -> {
                        submitEvent("TAKE " + object.getName());
                    });
                    objectsInRoom.getChildren().add(objectButton);
                }

                // Iterate through objects in the player's inventory and create ImageView elements for each
                for (int i = 0; i < this.model.getPlayer().inventory.size(); i++) {
                    AdventureObject object = this.model.getPlayer().inventory.get(i);
                    ImageView objectImageView = getImageView(i, true);
                    Button objectButton = new Button("", objectImageView);
                    makeButtonAccessible(objectButton, object.getName(), object.getDescription(), object.getDescription() + ". Click on the image to drop the object.");
                    VBox vbox = new VBox(objectImageView, new Text(object.getName()));
                    vbox.setAlignment(Pos.CENTER);
                    objectButton.setGraphic(vbox);
                    objectButton.setOnAction(e -> {
                        submitEvent("DROP " + object.getName());
                    });
                    objectsInInventory.getChildren().add(objectButton);
                }

                // Create a ScrollPane for displaying objects in the current room
                ScrollPane scO = new ScrollPane(objectsInRoom);
                scO.setPadding(new Insets(10));

                // Set styles for the ScrollPane
                scO.setStyle("-fx-background: #000000; -fx-background-color:transparent;");
                scO.setFitToWidth(true);

                // Add the ScrollPane to the gridPane at position (0, 1)
                gridPane.add(scO, 0, 1);

                // Create a ScrollPane for displaying objects in the player's inventory
                ScrollPane scI = new ScrollPane(objectsInInventory);
                scI.setFitToWidth(true);

                // Set styles for the ScrollPane
                scI.setStyle("-fx-background: #000000; -fx-background-color:transparent;");

                // Add the ScrollPane to the gridPane at position (2, 1)
                gridPane.add(scI, 2, 1);
            }
        });
    }

    /**
     * Returns an ImageView for the object at the specified index.
     * Checks whether to display an object in the current room or the player's inventory.
     * @param i
     * @param inventory
     * @return
     */
    private ImageView getImageView(int i, boolean inventory) {
        String objectName;

        // Determine whether we are updating inventory or objects in the current room
        if (inventory) {
            objectName = this.model.getPlayer().inventory.get(i).getName();
        } else {
            objectName = this.model.getPlayer().getCurrentRoom().objectsInRoom.get(i).getName();
        }

        // Construct the file path for the object's image
        String objectImage = this.model.getDirectoryName() + "/objectImages/" + objectName + ".jpg";

        // Load the object's image from the file
        Image objectImageFile = new Image(objectImage);

        // Create an ImageView and configure its properties
        ImageView objectImageView = new ImageView(objectImageFile);
        objectImageView.setPreserveRatio(true);
        objectImageView.setFitWidth(100);
        objectImageView.setFitHeight(75);
        objectImageView.setAccessibleRole(AccessibleRole.IMAGE_VIEW);

        // Set the accessible text for screen readers
        objectImageView.setAccessibleText(objectName);

        // Allow the ImageView to receive focus for accessibility
        objectImageView.setFocusTraversable(true);

        return objectImageView;
    }

    /**
     * Show the game instructions.
     *
     * If helpToggle is FALSE:
     * -- display the help text in the CENTRE of the gridPane (i.e. within cell 1,1)
     * -- use whatever GUI elements to get the job done!
     * -- set the helpToggle to TRUE
     * -- REMOVE whatever nodes are within the cell beforehand!
     *
     * If helpToggle is TRUE:
     * -- redraw the room image in the CENTRE of the gridPane (i.e. within cell 1,1)
     * -- set the helpToggle to FALSE
     * -- Again, REMOVE whatever nodes are within the cell beforehand!
     */
    public void showInstructions() {
        Platform.runLater(new Runnable() {
            @Override
            public void run() {
                Platform.setImplicitExit(false);
                if (!helpToggle) {
                    for (Button button : objectsInInventory.getChildren().toArray(new Button[0])) {
                        button.setDisable(true);
                    }
                    for (Button button : objectsInRoom.getChildren().toArray(new Button[0])) {
                        button.setDisable(true);
                    }
                    // Hide existing UI elements by setting their visibility to false
                    for (int i = 0; i < gridPane.getChildren().size(); i++) {
                        if (gridPane.getChildren().get(i).getProperties().get("gridpane-column").equals(1) &
                                gridPane.getChildren().get(i).getProperties().get("gridpane-row").equals(1)) {
                            gridPane.getChildren().get(i).setVisible(false);
                        }
                    }

                    // Create and display a VBox containing help information
                    Label helpLabel = new Label("Welcome to the Adventure Game!\n\n" +
                            "To play this game you must move between locations and interact with objects by\n typing one or two word commands.\n\n" +
                            "Some commands are motion commands. These will move you from room to\nroom. Motion commands include:\n\n" +
                            "UP, DOWN EAST, WEST, NORTH, SOUTH, IN, OUT\n\n" +
                            "Not all motions are possible in every room. In addition, some rooms may have \n 'special' or 'secret' motion commands.\n\n" +
                            "There are other action commands in the game. These include:\n\n" +
                            "COMMANDS: Print a list of legal moves in the given room. \n" +
                            "LOOK <object>: Look around the room.\n" +
                            "TAKE <object>: Take an object.\n" +
                            "DROP <object>: Drop an object.\n" +
                            "INVENTORY <object>: View your inventory.\n" +
                            "HELP <object>: View these instructions.\n" +
                            "QUIT <object>: Quit the game.\n\n" +
                            "Good luck!");
                    helpLabel.setStyle("-fx-text-fill: white;");
                    helpLabel.setFont(new Font("Arial", 16));
                    helpLabel.setAlignment(Pos.CENTER);
                    VBox helpBox = new VBox(helpLabel);
                    helpBox.setAlignment(Pos.CENTER);
                    helpBox.setId("helpBox");
                    gridPane.add(helpBox, 1, 1);


                    // Set the helpToggle flag to true
                    helpToggle = true;
                } else {
                    // Restore the previous view by showing existing UI elements
                    stopArticulation();
                    articulateRoomDescription();
                    for (Button button : objectsInInventory.getChildren().toArray(new Button[0])) {
                        button.setDisable(false);
                    }
                    for (Button button : objectsInRoom.getChildren().toArray(new Button[0])) {
                        button.setDisable(false);
                    }
                    for (int i = 0; i < gridPane.getChildren().size(); i++) {
                        if (gridPane.getChildren().get(i).getProperties().get("gridpane-column").equals(1) &
                                gridPane.getChildren().get(i).getProperties().get("gridpane-row").equals(1)) {
                            gridPane.getChildren().get(i).setVisible(true);
                            if (gridPane.getChildren().get(i).getId() == "helpBox") {
                                gridPane.getChildren().remove(i);
                            }
                        }
                    }
                    displayRoomDescription();
                    // Set the helpToggle flag to false
                    helpToggle = false;
                }
            }
        });
    }

    /**
     * This method handles the event related to the
     * help button.
     */
    public void addInstructionEvent() {
        helpButton.setOnAction(e -> {
            stopArticulation(); //if speaking, stop
            showInstructions();
        });
    }

    /**
     * This method handles the event related to the
     * save button.
     */
    public void addSaveEvent() {
        saveButton.setOnAction(e -> {
            gridPane.requestFocus();
            SaveView saveView = new SaveView(this);
        });
    }

    /**
     * This method handles the event related to the
     * load button.
     */
    public void addLoadEvent() {
        loadButton.setOnAction(e -> {
            gridPane.requestFocus();
            LoadView loadView = new LoadView(this);
        });
    }


    /**
     * This method articulates Room Descriptions
     */
    public void articulateRoomDescription() {
        String musicFile;
        String adventureName = this.model.getDirectoryName();
        String roomName = this.model.getPlayer().getCurrentRoom().getRoomName();

        if (!this.model.getPlayer().getCurrentRoom().getVisited()) musicFile = "./" + adventureName + "/sounds/" + roomName.toLowerCase() + "-long.mp3" ;
        else musicFile = "./" + adventureName + "/sounds/" + roomName.toLowerCase() + "-short.mp3" ;
        musicFile = musicFile.replace(" ","-");

        Media sound = new Media(new File(musicFile).toURI().toString());

        mediaPlayer = new MediaPlayer(sound);
        mediaPlayer.play();
        mediaPlaying = true;

    }

    /**
     * This method stops articulations
     * (useful when transitioning to a new room or loading a new game)
     */
    public void stopArticulation() {
        if (mediaPlaying) {
            mediaPlayer.stop(); //shush!
            mediaPlaying = false;
        }
    }

    /**
     * This method displays the room description
     * (useful when transitioning to a new room or loading a new game)
     */
    public void displayRoomDescription()
    {
        // Get the current room's description
        String roomDesc = this.model.getPlayer().getCurrentRoom().getRoomDescription() + "\n";

        // Get a string representation of objects in the current room
        String objectString = this.model.getPlayer().getCurrentRoom().getObjectString();

        // Check if there are objects in the room
        if (!objectString.isEmpty()) {
            // Set the room description label with both room description and object information
            updateScene(roomDesc + "\n\nObjects in this room:\n" + objectString);
        } else {
            // Set the room description label with only the room description
            updateScene(roomDesc);
        }
    }

    /**
     * This method checks for forced moves
     *
     * If motion table contains forced move to room 0, GAME OVER
     * Else, FORCED
     */
    public void checkForcedMoves() {
        if (this.model.getPlayer().getCurrentRoom().getMotionTable().getDirection().get(0).getDestinationRoom() == 0) {
            updateScene("");
            updateItems();
            PauseTransition pause = new PauseTransition(Duration.seconds(10));
            pause.setOnFinished(event -> {
                if (model.player.getCurrentRoom().getRoomNumber() == 0)
                {
                    Platform.exit();
                }
            });
            pause.play();
        } else if (this.model.getPlayer().getCurrentRoom().getMotionTable().getDirection().get(0).getDirection().equals("FORCED")) {
            //forced move that is not game over
            updateScene("");
            updateItems();
            // after pause, move player to forced room and update scene
            PauseTransition pause = new PauseTransition(Duration.seconds(5));
            pause.setOnFinished(event -> {
                stopArticulation();
                articulateRoomDescription();
                updateItems();
                displayRoomDescription();
                submitEvent("FORCED");
            });
            pause.play();
        }
    }
}

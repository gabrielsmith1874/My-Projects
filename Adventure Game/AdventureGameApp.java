import AdventureModel.AdventureGame;
import javafx.application.Application;
import javafx.stage.Stage;
import views.AdventureGameView;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.io.IOException;
import javafx.scene.Scene;
import javafx.scene.image.Image;

/**
 * Class AdventureGameApp.
 */
public class AdventureGameApp extends  Application {
    AdventureGame model;
    AdventureGameView view;

    /*
    * JavaFX is a Framework, and to use it we will have to
    * respect its control flow!  To start the game, we need
    * to call "launch" which will in turn call "start" ...
     */
    @Override
    public void start(Stage primaryStage) throws IOException {
        try {
            // Model
            this.model = new AdventureGame("TinyGame"); //change the name of the game if you want to try something bigger!
            this.view = new AdventureGameView(model, primaryStage);
        } catch (Exception ex) {
            Logger.getLogger(getClass().getName()).log(Level.SEVERE, " Error loading the Main class", ex);
        }
    }
    public static void main(String[] args) {
        launch(args);
    }

}

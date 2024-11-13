#include <stdio.h>
#include <stdlib.h>

// Function to remove vocals from a wav file and save the result to another wav file
void remvocals(char *sourcewav, char *destwav)
{
    // Declare variables
    FILE *fp1, *fp2;
    char header[44];  // Use an array to store the header

    // Open the source wav file for reading in binary mode
    fp1 = fopen(sourcewav, "rb");

    // Check if the file opened successfully
    if (fp1 == NULL) {
        printf("Error in opening the source file\n");
        exit(1);
    }

    // Open the destination wav file for writing in binary mode
    fp2 = fopen(destwav, "wb");

    // Check if the destination file opened successfully
    if (fp2 == NULL) {
        printf("Error in opening the destination file\n");

        // Close the source file before exiting
        fclose(fp1);
        exit(1);
    }

    // Copy the first 44 bytes (header) from the source file to the destination file
    fread(header, 1, sizeof(header), fp1);
    fwrite(header, 1, sizeof(header), fp2);

    // Process the audio data to remove vocals
    while (!feof(fp1)) {
        short int left, right;

        // Read left and right channel values from the source file
        fread(&left, sizeof(short int), 1, fp1);
        fread(&right, sizeof(short int), 1, fp1);

        // Remove vocals by subtracting the right channel from the left and dividing by 2
        left = (left - right) / 2;
        right = left;

        // Write modified left and right channel values to the destination file
        fwrite(&left, sizeof(short int), 1, fp2);
        fwrite(&right, sizeof(short int), 1, fp2);
    }

    // Close both source and destination files
    fclose(fp1);
    fclose(fp2);
}


int main(int argc, char *argv[]) {
    // Check if the number of arguments is correct
    if (argc != 3) {
        printf("Usage: %s <sourcewav> <destwav>\n", argv[0]);
        return 1;
    }

    // Call the remvocals function to remove vocals from the source wav file
    remvocals(argv[1], argv[2]);

    return 0;
    
}

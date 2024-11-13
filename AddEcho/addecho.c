#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define HEADER_SIZE 22

// Function to print usage instructions
void print_usage() {
    fprintf(stderr, "Usage: addecho [-d delay] [-v volume_scale]  <sourcewave> <destwave>\n");
}

// Function to add echo to a wave file
void addecho(FILE *inputFile, FILE *outputFile, int delay, int volumeScale) {
    // Create a wave header struct
    struct HEADER {
        char riff[4];
        int chunk_size;
        char wave[4];
        char fmt[4];
        int subchunk1_size;
        short audio_format;
        short num_channels;
        int sample_rate;
        int byte_rate;
        short block_align;
        short bits_per_sample;
        char data[4];
        int subchunk2_size;
    } waveHeader;

    // Check if files are open
    if (inputFile == NULL || outputFile == NULL) {
        printf("Error: Unable to open file\n");
        return;
    }

    // Read the wave file header
    fread(&waveHeader, sizeof(waveHeader), 1, inputFile);
    waveHeader.subchunk2_size += delay * 2;
    waveHeader.chunk_size += delay * 2;
    fwrite(&waveHeader, sizeof(waveHeader), 1, outputFile);

    // Create an echo buffer
    short *echoBuffer = (short *)malloc(delay * sizeof(short));
    short originalSample[1];
    int numSamples  = 0;
    int echoIndex = 0;

    // Read the wave file and add echo
    while((fread(originalSample, sizeof(short), 1, inputFile)) > 0) {
        if (numSamples < delay) {
            fwrite(originalSample, sizeof(short), 1, outputFile);
            echoBuffer[numSamples] = (originalSample[0]/volumeScale);
        } else {
            if (echoIndex  == delay) {
                echoIndex  = 0;
            }
            short newSample = originalSample[0];
            originalSample[0] += echoBuffer[echoIndex];
            echoBuffer[echoIndex] = (newSample/volumeScale);
            echoIndex++;
            fwrite(originalSample, sizeof(short), 1, outputFile);
        }
        numSamples++;
    }

    // Pad the end of the file with zeros if delay exceeds the file length
    short emptySamples = 0;
    int remainingSamples = delay - numSamples;
    if (remainingSamples > 0) {
        for (int k=0; k < remainingSamples; k++)
            fwrite(&emptySamples, sizeof(emptySamples), 1, outputFile);
    }

    // Write the remaining echo buffer to the file
    if (remainingSamples > 0) {
        fwrite(echoBuffer, sizeof(short), numSamples, outputFile);
    } else {
        int diff = delay - echoIndex;
        fwrite(&echoBuffer[echoIndex], sizeof(short), diff, outputFile);
        fwrite(echoBuffer, sizeof(short), echoIndex, outputFile);
    }

    // Free the echo buffer and close the files
    free(echoBuffer);
    fclose(inputFile);
    fclose(outputFile);
}

int main(int argc, char *argv[]) {
    // Default values
    int delay = 8000;
    int volume_scale = 4;

    // Process command line arguments
    if (argc >= 4) {
        int i;
        for (i = 1; i < argc - 2; i++) {
            if (strcmp(argv[i], "-d") == 0) {
                int temp = atoi(argv[i + 1]);
                if (temp <= 0) {
                    print_usage();
                    return 1;
                }
                delay = temp;
                i++;
            } else if (strcmp(argv[i], "-v") == 0) {
                int temp = atoi(argv[i + 1]);
                if (temp <= 0) {
                    print_usage();
                    return 1;
                }
                volume_scale = temp;
                i++;
            }
        }
        //checks if the last two arguments are wav files
        if (i == argc - 2) {
            if (strstr(argv[1], ".wav") != NULL && strstr(argv[2], ".wav") != NULL) {
                FILE *inputFile = fopen_s(argv[i], "rb");
                FILE *outputFile = fopen_s(argv[i + 1], "wb");
                addecho(inputFile, outputFile, delay, volume_scale);
            }
        } else {
            print_usage();
            return 1;
        }
    }
    else
    {
        // default values
        if (argc == 3) {
            //check if arguments are wav files
            if (strstr(argv[1], ".wav") != NULL && strstr(argv[2], ".wav") != NULL) {
                FILE *inputFile = fopen(argv[1], "rb");
                FILE *outputFile = fopen(argv[2], "wb");
                addecho(inputFile, outputFile, delay, volume_scale);
            } else {
                print_usage();
                return 1;
            }
        }
        else
        {
            print_usage();
            return 1;
        }
    }
    return 0;
}
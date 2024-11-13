#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#define PORT 56041
#define BUFFER_SIZE 2048
#define MAXNAME 25
#define ANSI_COLOR_RED "\x1b[31m"
#define ANSI_COLOR_LIGHT_BLUE "\x1b[94m"
#define ANSI_COLOR_RESET "\x1b[0m"
#define HEALTH_DESCRIPTION "This Potion increases your health by 10 hp!\n"
#define POWER_DESCRIPTION "This Potion increases your powerMoves by 1!\n"
#define SHIELD_DESCRIPTION                                                     \
  "This potion reduces the next damage you take by half!\n"

struct client {
  int has_name;
  int speaking;
  char message[512];
  char name[MAXNAME];
  int fd;
  struct in_addr ipaddr;
  struct client *next;
  struct client *previous;
  struct client *lastbattled;
  struct client *opponent;
  int turn;
  int hp;
  int powermoves;
  char item[512];
  char item_description[512];
  int isShielded;
};

static struct client *addclient(struct client *top, int fd,
                                struct in_addr addr);
static struct client *removeclient(struct client *top, int fd);
static void broadcast(struct client *top, int fd, char *s, int size);
// static char *getResponse(int fd, char *buffer, int size);
int handleclient(struct client *p, struct client *top);
int bindandlisten(void);
int locate_newline(char *buf, int inbuf);
void pair_clients(struct client *p, struct client *head);
void perform_attack(struct client *a, struct client *b, struct client *top);
void perform_powermove(struct client *a, struct client *b, struct client *top);
void send_message(struct client *a, struct client *b);
void display_status(struct client *a, struct client *b);
void addRandomItem(struct client *p);
void handle_loss(struct client *a, struct client *b, struct client *top);
static int genRandInt(int min, int max);
void reset_client_list_head(struct client **head);
void pair_clients_in_list(struct client *head);
void handle_new_client_connection(struct client **head, fd_set *allSockets, int *maxSocket, int listenSocket);
void handle_client_data(struct client **head, fd_set *allSockets, int maxSocket, fd_set readSockets);
void handle_game_actions(struct client *p, struct client *top, char *buf);
void send_message_to_client(int fd, char *message);


int main(void) {
    // Seed the random number generator
    srand(time(NULL));

    // Initialize socket variables
    int listenSocket, maxSocket;
    fd_set allSockets, readSockets;

    // Initialize client list
    struct client *clientListHead = NULL;

    // Bind and listen for connections
    listenSocket = bindandlisten();

    // Initialize the set of active sockets
    FD_ZERO(&allSockets);
    FD_SET(listenSocket, &allSockets);
    maxSocket = listenSocket;

    // Main server loop
    while (1) {
        // Reset the head of the client list (if needed)
        reset_client_list_head(&clientListHead);

        // Pair clients for a battle
        pair_clients_in_list(clientListHead);

        // Copy the set of active sockets
        readSockets = allSockets;

        // Wait for something to happen on any of the sockets
        select(maxSocket + 1, &readSockets, NULL, NULL, NULL);

        // Check for new client connections
        if (FD_ISSET(listenSocket, &readSockets)) {
            handle_new_client_connection(&clientListHead, &allSockets, &maxSocket, listenSocket);
        }

        // Check for data on existing client sockets
        handle_client_data(&clientListHead, &allSockets, maxSocket, readSockets);
    }

    return 0;
}

void reset_client_list_head(struct client **head) {
    struct client *current = *head;
    while (current != NULL) {
        if (current->previous == NULL) {
            *head = current;
            break;
        }
        current = current->previous;
    }
}

void pair_clients_in_list(struct client *head) {
    // Count the number of clients
    int count = 0;
    struct client *current = head;
    while (current != NULL) {
        count++;
        current = current->next;
    }

    // Allocate an array for the clients
    struct client **clients = malloc(count * sizeof(struct client *));
    if (!clients) {
        perror("malloc");
        exit(1);
    }

    // Put the clients into the array
    current = head;
    for (int i = 0; i < count; i++) {
        clients[i] = current;
        current = current->next;
    }

    // Shuffle the array (Fisher-Yates shuffle)
    for (int i = count - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        struct client *temp = clients[i];
        clients[i] = clients[j];
        clients[j] = temp;
    }

    // Pair the clients
    for (int i = 0; i < count - 1; i += 2) {
        pair_clients(clients[i], clients[i + 1]);
    }

    // Free the array
    free(clients);

    struct client *current2 = head;
    while (current2 != NULL) {
        if (current2->opponent == NULL) {
            struct client *next = current2->next;
            while (next != NULL) {
                if (next->opponent == NULL) {
                    pair_clients(current2, next);
                    break;
                }
                next = next->next;
            }
        }
        current2 = current2->next;
    }
}

void handle_new_client_connection(struct client **head, fd_set *allSockets, int *maxSocket, int listenSocket) {
    struct sockaddr_in clientAddress;
    socklen_t clientAddressLength = sizeof(clientAddress);
    int newClientSocket = accept(listenSocket, (struct sockaddr *)&clientAddress, &clientAddressLength);

    if (newClientSocket < 0) {
        perror("accept");
        exit(1);
    }

    // Add the new client to the client list
    *head = addclient(*head, newClientSocket, clientAddress.sin_addr);

    // Add the new client socket to the set of active sockets
    FD_SET(newClientSocket, allSockets);

    // Update the maximum socket value
    if (newClientSocket > *maxSocket) {
        *maxSocket = newClientSocket;
    }
}

void handle_client_data(struct client **head, fd_set *allSockets, int maxSocket, fd_set readSockets) {
    struct client *current = *head;
    while (current != NULL) {
        if (FD_ISSET(current->fd, &readSockets)) {
            int result = handleclient(current, *head);
            if (result < 0) {
                // Remove the client from the client list
                *head = removeclient(*head, current->fd);

                // Remove the client socket from the set of active sockets
                FD_CLR(current->fd, allSockets);

                // Close the client socket
                close(current->fd);
            }
        }
        current = current->next;
    }
}

int handleclient(struct client *p, struct client *top) {
    // Buffer for reading client input
    char buf[256];

    // Buffer for output messages
    char outbuf[512];

    // Read client input
    int len = read(p->fd, buf, sizeof(buf) - 1);

    // If there is input
    if (len > 0) {
        // If client has not set a name yet
        if (!p->has_name) {
            // Append input to the name
            strncpy(&(*(p->name + strlen(p->name))), buf, 1);

            // Find the newline character in the name
            int end;
            if ((end = locate_newline(p->name, MAXNAME)) >= 0) {
                // If name is too long, notify the client
                if (end >= MAXNAME) {
                    if (write(p->fd, "Name was too long\n", 18) < 0) {
                        perror("write");
                        return -1;
                    }
                }

                // Welcome the client and broadcast their entrance
                char message[512];
                p->name[end] = '\0';
                int ret = snprintf(message, sizeof(message), "Welcome %s! Waiting for opponent...\n", p->name);
                if (ret < 0 || ret >= sizeof(message)) {
                    perror("snprintf");
                    return -1;
                }

                if (write(p->fd, message, strlen(message)) < 0) {
                    perror("write");
                    return -1;
                }

                ret = snprintf(message, sizeof(message), "*** %s enters the arena ***\n", p->name);
                if (ret < 0 || ret >= sizeof(message)) {
                    perror("snprintf");
                    return -1;
                }

                broadcast(top, p->fd, message, strlen(message));
                p->has_name = 1;
            }
            return 0;
        }
            // If client is speaking
        else if (p->speaking) {
            // Copy the input to the message
            strncpy(p->message, buf, len);

            // Read the rest of the message until newline
            char out_str1[3]; // Buffer for reading the rest of the message
            int response;
            do {
                response = recv(p->fd, out_str1, sizeof(out_str1) - 1, 0);
                if (response > 0) {
                    out_str1[response] = '\0';
                    strcat(p->message, out_str1);
                }
            } while (response > 0 && strcmp(out_str1, "\n") != 0);

            // Send the message to the opponent
            send_message(p, p->opponent);

            // Reset the message and speaking status
            strcpy(p->message, "\0");
            p->speaking = 0;

            // Display the status of the game
            display_status(p, p->opponent);
            return 0;
        }
            // If client has an opponent
        else if (p->opponent != NULL) {
            // Handle game actions here
            handle_game_actions(p, top, buf);
        }
    }
        // If client disconnected
    else if (len == 0) {
        printf("Disconnect from %s\n", inet_ntoa(p->ipaddr));
        sprintf(outbuf, "%s has left the arena\n", p->name);
        broadcast(top, p->fd, outbuf, strlen(outbuf));
        return -1;
    }
        // If there was an error reading the input
    else {
        perror("read");
        return -1;
    }

    return 0;
}

void handle_game_actions(struct client *p, struct client *top, char *buf) {
    if (p->turn) {
        if (buf[0] == 'a') {
            p->turn = 0;
            p->opponent->turn = 1;
            addRandomItem(p);
            perform_attack(p, p->opponent, top);
            if (p->opponent != NULL) {
                display_status(p->opponent, p);
            }
            return;

        } else if (buf[0] == 'p') {
            if (p->powermoves == 0) {
                write(p->fd, "\nYou have no power moves left!\n", strlen("\nYou have no power moves left!\n"));
                return;
            }
            p->turn = 0;
            p->opponent->turn = 1;
            perform_powermove(p, p->opponent, top);
            if (p->opponent != NULL) {
                display_status(p->opponent, p);
            }
            return;

        } else if (buf[0] == 's') {
            write(p->fd, "\nPress enter to send your message: \n",
                  strlen("\nPress enter to send your message: \n"));
            p->speaking = 1;
            return;
        } else if (buf[0] == 'u' && strcmp(p->item, "None")) {
            char item[BUFFER_SIZE];
            sprintf(item, "\n%s used a [%s]!\n", p->name, p->item);
            write(p->fd, item, strlen(item));
            write(p->opponent->fd, item, strlen(item));
            if (!strcmp(p->item, "HEALTH POTION")) {
                p->hp += 10;
            } else if (!strcmp(p->item, "SHIELD POTION")) {
                p->isShielded = 1;
            } else if (!strcmp(p->item, "STRENGTH POTION")) {
                p->powermoves += 1;
            }
            if (!strcmp(p->item, "SHIELD POTION")) {
                strcpy(p->item, "None");
                strcpy(p->item_description, "None");
                display_status(p, p->opponent);
            } else {
                p->turn = 0;
                p->opponent->turn = 1;
                display_status(p->opponent, p);
            }
        }
        strcpy(p->item, "None");
        strcpy(p->item_description, "None");
        return;
    }
}

void pair_clients(struct client *p, struct client *head) {
    char message[512];
    struct client *t;
    for (t = head; t; t = t->next) {
        // Check if clients are eligible to be paired
        if ((t != p) && (p->has_name) && (t->has_name) && (p->opponent == NULL) &&
            (t->opponent == NULL) && ((t->lastbattled != p) || (p->lastbattled != t))) {

            // Pair the clients
            p->opponent = t;
            t->opponent = p;

            // Initialize game state
            p->hp = genRandInt(11, 30);
            p->powermoves = genRandInt(1, 2);
            t->hp = genRandInt(11, 30);
            t->powermoves = genRandInt(1, 2);
            p->speaking = 0;
            t->speaking = 0;
            strcpy(p->item, "None");
            strcpy(t->item, "None");
            strcpy(p->item_description, "None");
            strcpy(t->item_description, "None");
            p->isShielded = 0;
            t->isShielded = 0;

            // Send messages to the clients
            int ret = snprintf(message, sizeof(message), "You engage %s!\n", t->name);
            if (ret < 0 || ret >= sizeof(message)) {
                perror("snprintf");
                return;
            }
            write(p->fd, message, strlen(message));

            ret = snprintf(message, sizeof(message), "You engage %s!\n", p->name);
            if (ret < 0 || ret >= sizeof(message)) {
                perror("snprintf");
                return;
            }
            write(t->fd, message, strlen(message));

            // Decide who goes first
            int first = rand() % 2;
            if (first) {
                p->turn = 1;
                t->turn = 0;
                display_status(p, t);
            } else {
                p->turn = 0;
                t->turn = 1;
                display_status(t, p);
            }
        }
    }
}

void addRandomItem(struct client *p) {
    int item = genRandInt(1, 3);
    if (item == 1) {
        strcpy(p->item, "HEALTH POTION");
        strcpy(p->item_description, HEALTH_DESCRIPTION);
    } else if (item == 2) {
        strcpy(p->item, "SHIELD POTION");
        strcpy(p->item_description, SHIELD_DESCRIPTION);
    } else if (item == 3) {
        strcpy(p->item, "STRENGTH POTION");
        strcpy(p->item_description, POWER_DESCRIPTION);
    }
}

void display_status(struct client *a, struct client *b) {
    if (a->hp <= 0) {
        a->hp = 0;
    }
    if (b->hp <= 0) {
        b->hp = 0;
    }
    char message[BUFFER_SIZE];
    snprintf(message, sizeof(message),
             ANSI_COLOR_RED
             "\nYou have %d hitpoints and %d powermoves\n" ANSI_COLOR_RESET,
             a->hp, a->powermoves);
    send_message_to_client(a->fd, message);

    snprintf(message, sizeof(message), ANSI_COLOR_RED "%s has %d hitpoints\n" ANSI_COLOR_RESET,
             b->name, b->hp);
    send_message_to_client(a->fd, message);

    snprintf(message, sizeof(message), ANSI_COLOR_RED "\nYou have %d hitpoints\n" ANSI_COLOR_RESET,
             b->hp);
    send_message_to_client(b->fd, message);

    snprintf(message, sizeof(message),
             ANSI_COLOR_RED
             "\nYour items: %s - Description: %s\n" ANSI_COLOR_RESET,
             a->item, a->item_description);
    send_message_to_client(a->fd, message);

    snprintf(message, sizeof(message),
             ANSI_COLOR_LIGHT_BLUE "\nIt's your turn!\n" ANSI_COLOR_RESET);
    send_message_to_client(a->fd, message);

    snprintf(message, sizeof(message), ANSI_COLOR_LIGHT_BLUE "\nIt's %s' turn!\n" ANSI_COLOR_RESET,
             a->name);
    send_message_to_client(b->fd, message);

    send_message_to_client(a->fd,
                           ANSI_COLOR_LIGHT_BLUE "\n(a)ttack\n(p)owermove\n(s)peak\n(u)"
                           "se item\n\n" ANSI_COLOR_RESET);

    snprintf(message, sizeof(message),
             ANSI_COLOR_LIGHT_BLUE
             "Waiting for %s to end turn\n\n" ANSI_COLOR_RESET,
             a->name);
    send_message_to_client(b->fd, message);
}

void send_message_to_client(int fd, char *message) {
    write(fd, message, strlen(message));
}


void handle_loss(struct client *losingClient, struct client *winningClient, struct client *top) {
    // Define the messages for game result
    char *gameLostMessage = "You lost the game!\n";
    char *gameWonMessage = "You won the game!\n";

    // Check the health points of both clients
    if (winningClient->hp <= 0) {
        // If the winning client has no health points, they lost the game
        if (winningClient->fd != -1) {
            write(winningClient->fd, gameLostMessage, strlen(gameLostMessage));
        }
        if (losingClient->fd != -1) {
            write(losingClient->fd, gameWonMessage, strlen(gameWonMessage));
        }
    } else if (losingClient->hp <= 0) {
        // If the losing client has no health points, they lost the game
        if (winningClient->fd != -1) {
            write(winningClient->fd, gameWonMessage, strlen(gameWonMessage));
        }
        if (losingClient->fd != -1) {
            write(losingClient->fd, gameLostMessage, strlen(gameLostMessage));
        }
    }

    // Define the waiting message
    char *waitingMessage = "Waiting for opponent...\n";

    // Reset the game state for the winning client
    if (winningClient->fd != -1) {
        winningClient->lastbattled = losingClient;
        winningClient->opponent = NULL;
        write(winningClient->fd, waitingMessage, strlen(waitingMessage));
    }

    // Reset the game state for the losing client
    if (losingClient->fd != -1) {
        losingClient->lastbattled = winningClient;
        losingClient->opponent = NULL;
        write(losingClient->fd, waitingMessage, strlen(waitingMessage));
    }
}

void send_message(struct client *a, struct client *b) {
    fflush(stdout);
    char out_str[BUFFER_SIZE];
    sprintf(out_str, "%s says: %s", a->name, a->message);
    fflush(stdout);
    write(b->fd, out_str, strlen(out_str));

    const char *message_sent = "\nMessage sent.\n";
    write(a->fd, message_sent, strlen(message_sent));
    memset(a->message, 0, sizeof(a->message));
}

void perform_attack(struct client *a, struct client *b, struct client *top) {
    // Generate a random damage value between 2 and 6
    int damage = genRandInt(2, 6);

    // Check if the opponent has a shield
    if (b->isShielded) {
        // If the opponent is shielded, reduce the damage by half
        damage = damage / 2;

        // Prepare a message to notify both players about the shield
        char isShieldedbuf[BUFFER_SIZE];
        sprintf(isShieldedbuf, "%s is shielded! Damage reduced by half!\n", b->name);

        // Send the message to both players
        write(a->fd, isShieldedbuf, strlen(isShieldedbuf));
        write(b->fd, isShieldedbuf, strlen(isShieldedbuf));

        // Remove the shield from the opponent
        b->isShielded = 0;
    }

    // Apply the damage to the opponent's health points
    b->hp -= damage;

    // Prepare a message to notify the attacking player about the successful attack
    char attackMessage[BUFFER_SIZE];
    sprintf(attackMessage, "\nYou attacked %s and dealt %d damage!\n", b->name, damage);

    // Send the message to the attacking player
    write(a->fd, attackMessage, strlen(attackMessage));

    // Prepare a message to notify the opponent about the received damage
    sprintf(attackMessage, "\n%s attacked! You took %d damage!\n", a->name, damage);

    // Send the message to the opponent
    write(b->fd, attackMessage, strlen(attackMessage));

    // Check if any of the players has lost all health points
    if (b->hp <= 0) {
        // If the opponent has lost all health points, handle the loss
        handle_loss(a, b, top);
    } else if (a->hp <= 0) {
        // If the attacking player has lost all health points, handle the loss
        handle_loss(b, a, top);
    }
}

void perform_powermove(struct client *a, struct client *b, struct client *top) {
    // Generate a random damage value between 6 and 15
    int damage = genRandInt(6, 18);

    // Generate a random number to decide if the attack will hit or miss
    int attackProbability = genRandInt(0, 1);

    // If the attack misses
    if (attackProbability == 0) {
        // Prepare a message to notify both players about the missed attack
        char missedMessage[BUFFER_SIZE];
        sprintf(missedMessage, "\nYou missed! You dealt 0 damage!\n");
        write(a->fd, missedMessage, strlen(missedMessage));
        sprintf(missedMessage, "\n%s missed! You took 0 damage!\n", a->name);
        write(b->fd, missedMessage, strlen(missedMessage));
    }
        // If the attack hits
    else {
        // Apply the damage to the opponent's health points
        b->hp -= damage;

        // Prepare a message to notify the attacking player about the successful attack
        char attackMessage[BUFFER_SIZE];
        sprintf(attackMessage, "\nYou used a power move on %s and dealt %d damage!\n", b->name, damage);
        write(a->fd, attackMessage, strlen(attackMessage));

        // Prepare a message to notify the opponent about the received damage
        sprintf(attackMessage, "\n%s used a power move! You took %d damage!\n", a->name, damage);
        write(b->fd, attackMessage, strlen(attackMessage));

        // Decrease the number of power moves of the attacking player
        a->powermoves--;

        // Check if any of the players has lost all health points
        if (b->hp <= 0) {
            // If the opponent has lost all health points, handle the loss
            handle_loss(a, b, top);
        } else if (a->hp <= 0) {
            // If the attacking player has lost all health points, handle the loss
            handle_loss(b, a, top);
        }
    }
}

int bindandlisten(void) {
    struct sockaddr_in r;
    int listenSocket;

    // Create the socket
    if ((listenSocket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket");
        exit(1);
    }

    // Initialize the socket structure
    memset(&r, 0, sizeof(r));
    r.sin_family = AF_INET;
    r.sin_addr.s_addr = INADDR_ANY;
    r.sin_port = htons(PORT);

    // Bind the socket to the port
    if (bind(listenSocket, (struct sockaddr *)&r, sizeof(r)) < 0) {
        perror("bind");
        exit(1);
    }

    // Listen for connections
    if (listen(listenSocket, 5) < 0) {
        perror("listen");
        exit(1);
    }

    return listenSocket;
}

static struct client *addclient(struct client *top, int fd, struct in_addr addr) {
    // Allocate memory for the new client
    struct client *p = malloc(sizeof(struct client));
    if (!p) {
        perror("malloc");
        exit(1);
    }

    // Send a welcome message to the client
    write(fd, "What is your name? ", 20);

    // Initialize the client's properties
    p->fd = fd;
    p->ipaddr = addr;
    p->has_name = 0;
    p->opponent = NULL;
    p->next = NULL;

    // If the client list is empty, add the new client as the first client
    if (top == NULL) {
        p->previous = NULL;
        top = p;
    } else {
        // Otherwise, add the new client to the end of the list
        struct client *t = top;
        while (t->next != NULL) {
            t = t->next;
        }
        p->previous = t;
        t->next = p;
    }

    // Check if the client was added correctly
    if (p == NULL) {
        perror("addclient");
        exit(1);
    }

    // Return the updated client list
    return top;
}

static struct client *removeclient(struct client *top, int fd) {
    struct client *p;

    // Find the client in the list and remove it
    for (p = top; p; p = p->next) {
        if (p->fd == fd) {
            // If the client has a name, clear it
            if (p->has_name) {
                memset(p->name, 0, sizeof(p->name));
            }

            // If the client is speaking, clear the message
            if (p->speaking) {
                memset(p->message, 0, sizeof(p->message));
            }

            // If the client has an opponent, handle the loss
            if (p->opponent != NULL) {
                p->hp = 0;
                p->fd = -1;
                handle_loss(p, p->opponent, top);
            }

            // Remove the client from the list
            if (p->previous == NULL) {
                top = p->next;
            } else {
                p->previous->next = p->next;
            }
            if (p->next != NULL) {
                p->next->previous = p->previous;
            }

            // Free the memory allocated for the client
            free(p);

            // Return the updated client list
            return top;
        }
    }

    fprintf(stderr, "Could not remove fd %d\n", fd);
    return top;
}

static void broadcast(struct client *top, int fd, char *s, int size) {
    struct client *p;
    for (p = top; p; p = p->next) {
        if (p->fd != fd) {
            if (write(p->fd, s, size) == -1) {
                perror("write");
            }
        }
    }
}

int locate_newline(char *buf, int inbuf) {
    int i;
    for (i = 0; i < inbuf; i++) {
        if (buf[i] == '\n') {
            return i;
        }
    }
    return -1;
}

static int genRandInt(int min, int max) {
    return rand() % (max - min + 1) + min;
}

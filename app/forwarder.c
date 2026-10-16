/* Minimal CNF data-plane: packet counter/forwarder stand-in.
 * Real CNFs use DPDK/VPP/XDP; this mimics a C data-plane the healer monitors. */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>

static volatile int running = 1;
void on_term(int sig) { (void)sig; running = 0; }

int main(void) {
    signal(SIGTERM, on_term);
    signal(SIGINT, on_term);
    long packets = 0;
    printf("forwarder: starting (pid %d)\n", getpid());
    fflush(stdout);
    while (running) {
        packets++;
        if (packets % 10 == 0) {
            printf("forwarder: packets=%ld\n", packets);
            fflush(stdout);
        }
        usleep(200000); /* 5 pps */
    }
    printf("forwarder: shutting down packets=%ld\n", packets);
    return 0;
}

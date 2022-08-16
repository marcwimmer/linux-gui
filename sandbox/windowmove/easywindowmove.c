// vllt. moeglich um das window verschieben mit alt zu verbessern
#include <X11/extensions/XTest.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>
#include <stdbool.h>

int main() {
    Display *display = XOpenDisplay(nullptr);

    int kfd = open("/dev/input/event0", O_RDONLY);
    int tfd = open("/dev/input/event5", O_RDONLY);
    int mfd = kfd;
    if (tfd>mfd) mfd = tfd;
    bool leftAltDown = false;
    bool leftWinDown = false;
    bool touch = false;
    bool leftClickStateOnServer = false;
    bool rightClickStateOnServer = false;
    for (;;) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(kfd, &readfds);
        FD_SET(tfd, &readfds);
        int e = select(mfd+1, &readfds, nullptr, nullptr, nullptr);
        if (e>=0) {
            if (FD_ISSET(kfd, &readfds)) {
                input_event e;
                if (read(kfd, &e, sizeof(e))==sizeof(e)) {
                    if (e.type==EV_KEY) {
                        if (e.code==56) leftAltDown = e.value;
                        if (e.code==125) leftWinDown = e.value;
                    }
                }
            }
            if (FD_ISSET(tfd, &readfds)) {
                input_event e;
                read(tfd, &e, sizeof(e));
                if (e.type==EV_KEY&&e.code==BTN_TOUCH) {
                    touch = e.value;
                }
            }
        }

        bool leftClick = leftAltDown&&touch;
        bool rightClick = leftWinDown&&touch;

        if (leftClickStateOnServer!=leftClick) {
            leftClickStateOnServer = leftClick;
            XTestFakeButtonEvent(display, Button1, leftClick, CurrentTime);
            XSync(display, false);
        }
        if (rightClickStateOnServer!=rightClick) {
            rightClickStateOnServer = rightClick;
            XTestFakeButtonEvent(display, Button3, rightClick, CurrentTime);
            XSync(display, false);
        }
    }
}
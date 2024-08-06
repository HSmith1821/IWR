#include <stdio.h>
#include <string.h>
#include <fcntl.h>      // File controls
#include <errno.h>      
#include <termios.h>    // POSIX
#include <unistd.h>     // write, read, close
#include <sys/stat.h>   // Permissions

class Radar {
    public:
        Radar();
        ~Radar();

        void open();
    private:
        
};
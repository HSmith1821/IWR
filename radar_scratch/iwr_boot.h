#include <stdio.h>
#include <iostream>
#include <string.h>
#include <fcntl.h>      // File controls
#include <errno.h>      
#include <termios.h>    // POSIX
#include <unistd.h>     // write, read, close
#include <sys/stat.h>   // Permissions
#include <iomanip>


class Radar {
    public:
        Radar();
        ~Radar();

        void Open();
        void Close();
        void Read();
    private:
        int serial_port_config;
        int serial_port_data;
        const char *serial_port_data_name = "/dev/ttyACM1";
        const char *serial_port_config_name = "/dev/ttyACM0";
        unsigned char UART_MAGIC_WORD[9] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, '\0'};

};
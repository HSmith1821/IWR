#include <stdio.h>
#include <iostream>
#include <string.h>
#include <fcntl.h>      // File controls
#include <errno.h>      
#include <termios.h>    // POSIX
#include <unistd.h>     // write, read, close
#include <sys/stat.h>   // Permissions
#include <iomanip>
#include <vector>
#include <libudev.h>
#include <nlohmann/json.hpp>


class Radar {
    private:
        int serial_port_config;
        int serial_port_data;
        const char *serial_port_data_name = "/dev/ttyACM1";
        const char *serial_port_config_name = "/dev/ttyACM0";
        unsigned char UART_MAGIC_WORD[9] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, '\0'};
    protected:
        nlohmann::json m_config;
    public:
        /// @brief Constructor for Radar Class
        /// @param t_config JSON object containing config settings for radar
        Radar(nlohmann::json t_config);
        ~Radar();

        void Open();
        void Close();
        int16_t Read();
        void _start_many_radar();
        char* get_TI_ports();

};
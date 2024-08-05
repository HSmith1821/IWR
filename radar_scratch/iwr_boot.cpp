/*
*   Code to boot the IWR1642boost device
*   
*   How booting up the sensor works at a high level:
*     1) open all the com ports and check which ones are the radar board
*     2) Of the valid ports sort them into data and config ports
*     3) Open all the config ports and qurry for the ID on the board
*     4) Once the correct Com port has been found flash a new config file that will have the board brodcast its ID over the data port
*     5) Open all the data ports and listen for the ID
*     6) Once the correct port has been found reconfig the board for operation
*     7) close the config port and open the data port that is now streaming radar data

*/

/* To do: 
*   get rid of variable (ex. int) declarations and include in .h file instead 
*/




#include <stdio.h>
#include <string.h>
#include <fcntl.h>      // File controls
#include <errno.h>      
#include <termios.h>    // POSIX
#include <unistd.h>     // write, read, close
#include <sys/stat.h>   // Permissions

//"device_name": 'Radar_1',
#define BAUDRATE B921600
#define CONFIG_BAUDRATE B115200
#define ID 0x30d4da6e
#define save_type 'npy'
#define SAMPLING_RATE 30
#define dtype 'np.float32'
//'config_file': 'src/candor/cfg/radar_config_1642.cfg'
//'config_file_hr': 'src/candor/cfg/radar_config_1642_ht.cfg'
//'id_config_file': 'src/candor/cfg/id_radar_config_1642.cfg'
#define PRELOAD True
//'preload_json_path' :'src/candor/cfg/com_ports.json'
#define HARDWARE_TRIGGER False

int main() {

    /* To Do: Set Permissions for Serial Ports so all of them are accessible */


    /* To Do: instead of opening known Serial Port, go through com ports an find radar board */
    /* To Do: Determine automatically which ones are the data and config ports */
    int serial_port_config = open("/dev/ttyACM0", O_RDWR);
    if(serial_port_config < 0) {
        printf("Error %i opening configuation serial port: %s/n", errno, strerror(errno));
    }

    int serial_port_data = open("/dev/ttyACM1", O_RDWR);
    if(serial_port_data < 0) {
        printf("Error %i opening configuation serial port: %s/n", errno, strerror(errno));
    }

    /* To Do: Configure the serial ports to match the config file instead of being hardcoded */
    /* See termios documentation for structure */
    struct termios tty_config;
    if(tcgetattr(serial_port_config, &tty_config) != 0) {
        printf("Error %i getting tty_config attr: %s/n", errno, strerror(errno));
    }

    struct termios tty_data;
    if(tcgetattr(serial_port_data, &tty_data) != 0) {
        printf("Error %i getting tty_data attr: %s/n", errno, strerror(errno));
    }

    // More serial port configuration
    tty_data.c_cflag &= ~PARENB;
    tty_data.c_cflag &= ~CSTOPB;
    tty_data.c_cflag &= ~CSIZE;
    tty_data.c_cflag |= CS8;
    tty_data.c_cflag &= ~CRTSCTS;
    tty_config.c_cflag &= ~PARENB;
    tty_config.c_cflag &= ~CSTOPB;
    tty_config.c_cflag &= ~CSIZE;
    tty_config.c_cflag |= CS8;
    tty_config.c_cflag &= ~CRTSCTS;
    // Other port configuations?

    // Baud Rate Setup
    //cfsetispeed(&tty_data, BAUDRATE);
    //cfsetospeed(&tty_data, BAUDRATE);
    //cfsetispeed(&tty_config, CONFIG_BAUDRATE);
    //cfsetospeed(&tty_config, CONFIG_BAUDRATE);
    cfsetspeed(&tty_data, BAUDRATE);
    cfsetspeed(&tty_config, CONFIG_BAUDRATE);

    if(tcsetattr(serial_port_data, TCSANOW, &tty_data) != 0) {
        printf("Error %i setting tty_data attr: %s/n", errno, strerror(errno));
    }
    if(tcsetattr(serial_port_config, TCSANOW, &tty_config) != 0) {
        printf("Error %i setting tty_config attr: %s/n", errno, strerror(errno));
    }

    // Make this more streamlined for pulling data in real time
    // Temporary buffer? Queue?
    unsigned char data[128];
    while(1) {
        int n = read(serial_port_data, &data, sizeof(data));
        if(n > 0) {
            for(int i = 0; i < n; i++) {
                printf("%02x\n", data[i]);
            }   
        }
    }


    close(serial_port_data);
    close(serial_port_config);
}
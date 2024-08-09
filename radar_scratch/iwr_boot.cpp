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
*   Instead of defining variables, import cfg file (baud rate, cfg baud rate, ID, etc)
*/
#include "iwr_boot.h"

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


Radar::Radar() {
    /* TO DO
    *   Initialize settings from config file (preload)
    *   Setup hardware trigger
    *   Call open() function to initialize UART ports
    */
}

Radar::~Radar() {
    /* To Do: 
    *   
    */
    Close();
}

void Radar::Open(){
    /* To Do:
    *   ** For Now, just hardcode the values of the radar into the program **
    *
    *   if(preload)
            load the json config file
            make sure that the device is found in the preload JSON file
            Open the Serial Ports with Open()
        else
            {Look through all of the TI ports
            See which port (if any) matches the serial number
            if(board_found)
                write config file?
                check all data ports -> listen for serial number
                if(Data port found)
                    write real config file
                    Open serial ports with found info
            }
    */


    /* To Do: 
    *   Set Permissions for Serial Ports so all of them are accessible 
    *   Instead of opening known Serial Port, go through com ports an find radar board 
    *   Determine automatically which ones are the data and config ports 
    */

    serial_port_config = open(serial_port_config_name, O_RDWR);
    if(serial_port_config < 0) {
        printf("Error %i opening configuation serial port: %s/n", errno, strerror(errno));
    }

    serial_port_data = open(serial_port_data_name, O_RDWR);
    if(serial_port_data < 0) {
        printf("Error %i opening configuation serial port: %s/n", errno, strerror(errno));
    }

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
    cfsetspeed(&tty_data, BAUDRATE);
    cfsetspeed(&tty_config, CONFIG_BAUDRATE);

    if(tcsetattr(serial_port_data, TCSANOW, &tty_data) != 0) {
        printf("Error %i setting tty_data attr: %s/n", errno, strerror(errno));
    }
    if(tcsetattr(serial_port_config, TCSANOW, &tty_config) != 0) {
        printf("Error %i setting tty_config attr: %s/n", errno, strerror(errno));
    }

    std::cout << "Serial Ports Set up" << std::endl;

}


void Radar::Close(){
    close(serial_port_data);
    close(serial_port_config);
}


void Radar::Read(){
    unsigned char data[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, '\0'};
    unsigned char tmp;
    unsigned char byte[1];
    unsigned char range_bins[] = {0x00, 0x00, '\0'};
    std::cout << "Variables Initialized" << std::endl;

    // Look for the Magic Word at the start of the header
    while(memcmp(data, UART_MAGIC_WORD, sizeof(UART_MAGIC_WORD)) != 0)
    {
        //std::cout << int(data[1]) << std::endl;
        for(int i = 0; i < sizeof(data) - 2; i++){
            tmp = data[i];
            data[i] = data[i+1];
            //std::cout << data[i] << std::endl;
        }
        data[sizeof(data)] = tmp;
        int n = read(serial_port_data, &byte, 1);
        if(n < 0){
            printf("Error %i reading *HEADER* from serial: %s/n", errno, strerror(errno));
        }
        data[7] = byte[0];

        
        // Print for Debugging
        for(int z = 0; z < sizeof(data) - 1; z++)
        {
            std::cout << int(data[z]) << " ";
        }
        std::cout << std::endl;
        
    }

    std::cout << "Start to read # of bins" << std::endl;
    // Read the number of bins
    int n = read(serial_port_data, &range_bins, 2);
    if (n < 2 ){
        printf("Error %i setting tty_data attr: %s/n", errno, strerror(errno));
    }
    std::cout << "Got this far" << std::endl;
    //uint16_t range_bins_num = ((uint16_t)range_bins[0] << 8) | range_bins[1];   //two uint8 to one uint16

    //unsigned char data_frame[range_bins_num];
    
}





int main() {

    Radar radar = Radar();
    radar.Open();
    radar.Read();
    radar.Close();
    /* Basic function to just stream the data from the serial port to the terminal output */
    /*
    // Make this more streamlined for pulling data in real time
    // Temporary buffer? Queue?
    unsigned char data[128];
    while(1) {
        int n = read(serial_port_data, &data, 1); //sizeof(data));
        if(n > 0) {
            for(int i = 0; i < n; i++) {
                printf("%02x\n", data[i]);
            }   
        }
    }
    */

    /* Function to:
        * Initialize the configuration settings from the cfg file
        * Declare capture_directory
        * 
    */


}
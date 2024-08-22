#include <fstream>
#include <iostream>
#include "json_functions.h"

std::string readFile(const std::string &t_filename) {
    std::ifstream file{t_filename};
    if (!file.good()) {
        return {};
    }
    return std::string{std::istreambuf_iterator<char>{file}, {}};
}

void writeFile(const nlohmann::json &t_json_obj, const std::string &t_filename) {
    std::string json_obj = t_json_obj.dump(4);
    std::ofstream output_file(t_filename);
    if (output_file.is_open()) {
        output_file << json_obj;
        output_file.close();
        std::cout << "JSON object saved to " << t_filename << std::endl;
    } 
    else {
        std::cerr << "Unable to open " << t_filename << std::endl;
    }
}
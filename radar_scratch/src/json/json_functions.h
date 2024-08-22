#include <string>
#include "json.hpp"

/// @brief Read in a JSON object from a file
/// @param t_filename Name of the file you want to read the JSON object from
/// @return A stringified JSON object
std::string readFile(const std::string &t_filename);

/// @brief Write a json object to a file
/// @param t_json_obj JSON object you want to save
/// @param t_filename Name of the file you want to write the JSON object to
void writeFile(const nlohmann::json &t_json_obj, const std::string &t_filename);
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

struct HuffmanNode {
    std::uint8_t character = 0;
    std::uint64_t frequency = 0;
    std::uint16_t min_symbol = 0;
    std::uint64_t serial = 0;
    std::shared_ptr<HuffmanNode> left;
    std::shared_ptr<HuffmanNode> right;

    bool is_leaf() const { return !left && !right; }
};

using NodePtr = std::shared_ptr<HuffmanNode>;

struct NodeComparator {
    bool operator()(const NodePtr& a, const NodePtr& b) const {
        if (a->frequency != b->frequency) return a->frequency > b->frequency;
        if (a->min_symbol != b->min_symbol) return a->min_symbol > b->min_symbol;
        return a->serial > b->serial;
    }
};

class BitWriter {
public:
    void write_bit(bool bit) {
        if (bit) current_ |= static_cast<std::uint8_t>(1u << (7u - used_));
        ++used_;
        ++bit_count_;
        if (used_ == 8) {
            bytes_.push_back(current_);
            current_ = 0;
            used_ = 0;
        }
    }

    void write_byte(std::uint8_t value) {
        for (int shift = 7; shift >= 0; --shift) {
            write_bit(((value >> shift) & 1u) != 0);
        }
    }

    void finish() {
        if (used_ != 0) {
            bytes_.push_back(current_);  // Los bits no usados quedan en cero.
            current_ = 0;
            used_ = 0;
        }
    }

    const std::vector<std::uint8_t>& bytes() const { return bytes_; }
    std::uint64_t bit_count() const { return bit_count_; }

private:
    std::vector<std::uint8_t> bytes_;
    std::uint8_t current_ = 0;
    unsigned used_ = 0;
    std::uint64_t bit_count_ = 0;
};

class BitReader {
public:
    BitReader(const std::vector<std::uint8_t>& bytes, std::uint64_t bit_limit)
        : bytes_(bytes), bit_limit_(bit_limit) {
        if (bit_limit_ > static_cast<std::uint64_t>(bytes_.size()) * 8u) {
            throw std::runtime_error("El flujo de bits está truncado.");
        }
    }

    bool read_bit() {
        if (position_ >= bit_limit_) {
            throw std::runtime_error("Fin inesperado del flujo de bits.");
        }
        const std::size_t byte_index = static_cast<std::size_t>(position_ / 8u);
        const unsigned bit_index = static_cast<unsigned>(position_ % 8u);
        const bool value = ((bytes_[byte_index] >> (7u - bit_index)) & 1u) != 0;
        ++position_;
        return value;
    }

    std::uint8_t read_byte() {
        std::uint8_t value = 0;
        for (int i = 0; i < 8; ++i) {
            value = static_cast<std::uint8_t>((value << 1u) | (read_bit() ? 1u : 0u));
        }
        return value;
    }

    std::uint64_t position() const { return position_; }

private:
    const std::vector<std::uint8_t>& bytes_;
    std::uint64_t bit_limit_ = 0;
    std::uint64_t position_ = 0;
};

std::vector<std::uint8_t> read_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("No se pudo abrir el archivo de entrada: " + path.string());

    const std::streampos end = input.tellg();
    if (end < 0) throw std::runtime_error("No se pudo determinar el tamaño del archivo.");
    const auto size = static_cast<std::uint64_t>(end);
    if (size > std::numeric_limits<std::size_t>::max() ||
        size > static_cast<std::uint64_t>(std::numeric_limits<std::streamsize>::max())) {
        throw std::runtime_error("El archivo es demasiado grande para esta plataforma.");
    }

    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    input.seekg(0, std::ios::beg);
    if (!data.empty()) {
        input.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
        if (!input) throw std::runtime_error("Error al leer el archivo de entrada.");
    }
    return data;
}

void write_file(const fs::path& path, const std::vector<std::uint8_t>& data) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("No se pudo crear el archivo de salida: " + path.string());
    if (!data.empty()) {
        output.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
    }
    if (!output) throw std::runtime_error("Error al escribir el archivo de salida.");
}

NodePtr build_huffman_tree(const std::array<std::uint64_t, 256>& frequencies) {
    std::priority_queue<NodePtr, std::vector<NodePtr>, NodeComparator> min_heap;
    std::uint64_t serial = 0;

    for (unsigned symbol = 0; symbol < frequencies.size(); ++symbol) {
        if (frequencies[symbol] == 0) continue;
        auto leaf = std::make_shared<HuffmanNode>();
        leaf->character = static_cast<std::uint8_t>(symbol);
        leaf->frequency = frequencies[symbol];
        leaf->min_symbol = static_cast<std::uint16_t>(symbol);
        leaf->serial = serial++;
        min_heap.push(leaf);
    }

    if (min_heap.empty()) return nullptr;

    while (min_heap.size() > 1) {
        NodePtr left = min_heap.top();
        min_heap.pop();
        NodePtr right = min_heap.top();
        min_heap.pop();

        auto parent = std::make_shared<HuffmanNode>();
        parent->frequency = left->frequency + right->frequency;
        parent->min_symbol = std::min(left->min_symbol, right->min_symbol);
        parent->serial = serial++;
        parent->left = std::move(left);
        parent->right = std::move(right);
        min_heap.push(parent);
    }

    return min_heap.top();
}

void build_codes(const NodePtr& node, std::string& prefix,
                 std::array<std::string, 256>& codes) {
    if (!node) return;
    if (node->is_leaf()) {
        // Un código de un bit evita que un alfabeto unitario produzca un flujo vacío.
        codes[node->character] = prefix.empty() ? "0" : prefix;
        return;
    }

    prefix.push_back('0');
    build_codes(node->left, prefix, codes);
    prefix.back() = '1';
    build_codes(node->right, prefix, codes);
    prefix.pop_back();
}

void serialize_tree(const NodePtr& node, BitWriter& writer) {
    if (node->is_leaf()) {
        writer.write_bit(true);
        writer.write_byte(node->character);
        return;
    }
    writer.write_bit(false);
    serialize_tree(node->left, writer);
    serialize_tree(node->right, writer);
}

void append_u16_be(std::vector<std::uint8_t>& out, std::uint16_t value) {
    out.push_back(static_cast<std::uint8_t>((value >> 8u) & 0xffu));
    out.push_back(static_cast<std::uint8_t>(value & 0xffu));
}

void append_u64_be(std::vector<std::uint8_t>& out, std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(static_cast<std::uint8_t>((value >> shift) & 0xffu));
    }
}

std::uint16_t read_u16_be(const std::vector<std::uint8_t>& bytes, std::size_t offset) {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(bytes[offset]) << 8u) |
                                      static_cast<std::uint16_t>(bytes[offset + 1]));
}

std::uint64_t read_u64_be(const std::vector<std::uint8_t>& bytes, std::size_t offset) {
    std::uint64_t value = 0;
    for (std::size_t i = 0; i < 8; ++i) value = (value << 8u) | bytes[offset + i];
    return value;
}

std::uint64_t serialized_tree_bits(std::uint16_t symbol_count) {
    return symbol_count == 0 ? 0 : 10u * static_cast<std::uint64_t>(symbol_count) - 1u;
}

NodePtr deserialize_tree(BitReader& reader, std::array<bool, 256>& seen,
                         std::uint16_t expected_symbols, std::uint16_t& leaf_count,
                         unsigned depth = 0) {
    if (depth > 255) throw std::runtime_error("El árbol serializado excede la profundidad permitida.");

    if (reader.read_bit()) {
        const std::uint8_t symbol = reader.read_byte();
        if (seen[symbol]) throw std::runtime_error("El árbol contiene un símbolo duplicado.");
        if (leaf_count >= expected_symbols) throw std::runtime_error("El árbol contiene demasiadas hojas.");
        seen[symbol] = true;
        ++leaf_count;

        auto leaf = std::make_shared<HuffmanNode>();
        leaf->character = symbol;
        leaf->min_symbol = symbol;
        return leaf;
    }

    auto parent = std::make_shared<HuffmanNode>();
    parent->left = deserialize_tree(reader, seen, expected_symbols, leaf_count, depth + 1);
    parent->right = deserialize_tree(reader, seen, expected_symbols, leaf_count, depth + 1);
    return parent;
}

void compress_file(const fs::path& input_path, const fs::path& output_path) {
    const std::vector<std::uint8_t> input = read_file(input_path);
    std::array<std::uint64_t, 256> frequencies{};
    for (std::uint8_t byte : input) ++frequencies[byte];

    std::uint16_t symbol_count = 0;
    for (std::uint64_t frequency : frequencies) {
        if (frequency != 0) ++symbol_count;
    }

    const NodePtr root = build_huffman_tree(frequencies);
    std::array<std::string, 256> codes{};
    std::string prefix;
    if (root) build_codes(root, prefix, codes);

    BitWriter tree_writer;
    if (root) serialize_tree(root, tree_writer);
    tree_writer.finish();
    if (tree_writer.bit_count() != serialized_tree_bits(symbol_count)) {
        throw std::runtime_error("La longitud del árbol serializado no coincide con su alfabeto.");
    }

    BitWriter payload_writer;
    for (std::uint8_t byte : input) {
        for (char bit : codes[byte]) payload_writer.write_bit(bit == '1');
    }
    payload_writer.finish();

    std::vector<std::uint8_t> output{'H', 'U', 'F', '1'};
    append_u64_be(output, static_cast<std::uint64_t>(input.size()));
    append_u16_be(output, symbol_count);
    output.insert(output.end(), tree_writer.bytes().begin(), tree_writer.bytes().end());
    output.insert(output.end(), payload_writer.bytes().begin(), payload_writer.bytes().end());
    write_file(output_path, output);
}

void decompress_file(const fs::path& input_path, const fs::path& output_path) {
    const std::vector<std::uint8_t> file = read_file(input_path);
    constexpr std::size_t header_size = 14;
    if (file.size() < header_size) throw std::runtime_error("El archivo comprimido no contiene una cabecera completa.");
    if (file[0] != 'H' || file[1] != 'U' || file[2] != 'F' || file[3] != '1') {
        throw std::runtime_error("La firma del archivo no es HUF1.");
    }

    const std::uint64_t original_size = read_u64_be(file, 4);
    const std::uint16_t symbol_count = read_u16_be(file, 12);
    if (symbol_count > 256) throw std::runtime_error("La cabecera declara más de 256 símbolos.");
    if ((original_size == 0) != (symbol_count == 0)) {
        throw std::runtime_error("El tamaño original y el alfabeto declarado son inconsistentes.");
    }
    if (original_size > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("El archivo descomprimido no cabe en la memoria de esta plataforma.");
    }

    const std::uint64_t tree_bits = serialized_tree_bits(symbol_count);
    const std::size_t tree_bytes = static_cast<std::size_t>((tree_bits + 7u) / 8u);
    if (file.size() - header_size < tree_bytes) throw std::runtime_error("El árbol de Huffman está truncado.");

    NodePtr root;
    std::size_t payload_offset = header_size + tree_bytes;
    if (symbol_count != 0) {
        std::vector<std::uint8_t> tree_data(file.begin() + static_cast<std::ptrdiff_t>(header_size),
                                            file.begin() + static_cast<std::ptrdiff_t>(payload_offset));
        BitReader tree_reader(tree_data, tree_bits);
        std::array<bool, 256> seen{};
        std::uint16_t leaf_count = 0;
        root = deserialize_tree(tree_reader, seen, symbol_count, leaf_count);
        if (leaf_count != symbol_count || tree_reader.position() != tree_bits) {
            throw std::runtime_error("El árbol serializado no coincide con el número de símbolos.");
        }
    }

    std::vector<std::uint8_t> payload(file.begin() + static_cast<std::ptrdiff_t>(payload_offset), file.end());
    const std::uint64_t payload_bit_limit = static_cast<std::uint64_t>(payload.size()) * 8u;
    BitReader payload_reader(payload, payload_bit_limit);
    std::vector<std::uint8_t> decoded;
    decoded.reserve(static_cast<std::size_t>(original_size));

    if (root && root->is_leaf()) {
        for (std::uint64_t i = 0; i < original_size; ++i) {
            if (payload_reader.read_bit()) throw std::runtime_error("Código inválido para un alfabeto de un símbolo.");
            decoded.push_back(root->character);
        }
    } else if (root) {
        for (std::uint64_t i = 0; i < original_size; ++i) {
            NodePtr current = root;
            while (!current->is_leaf()) {
                current = payload_reader.read_bit() ? current->right : current->left;
                if (!current) throw std::runtime_error("El flujo de bits apunta a una rama inexistente.");
            }
            decoded.push_back(current->character);
        }
    }

    if (decoded.size() != original_size) throw std::runtime_error("La salida no coincide con el tamaño original declarado.");
    write_file(output_path, decoded);
}

void print_usage(const char* executable) {
    std::cerr << "Uso:\n"
              << "  " << executable << " compress <entrada> <salida.huf>\n"
              << "  " << executable << " decompress <entrada.huf> <salida>\n";
}

int main(int argc, char** argv) {
    if (argc != 4) {
        print_usage(argv[0]);
        return 2;
    }

    try {
        const std::string command = argv[1];
        if (command == "compress") {
            compress_file(argv[2], argv[3]);
        } else if (command == "decompress") {
            decompress_file(argv[2], argv[3]);
        } else {
            print_usage(argv[0]);
            return 2;
        }
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}

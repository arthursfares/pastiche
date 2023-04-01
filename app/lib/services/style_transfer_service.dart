import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class StyleTransferService {
  StyleTransferService();

  final apiUrl = 'http://127.0.0.1:8000/transfer-style/';

  Future<Uint8List> transferStyle(Map<String, dynamic> request) async {
    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(request),
      );
      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        throw Exception('Failed to transfer style');
      }
    } catch (error) {
      throw Exception('Failed to transfer style: $error');
    }
  }
}

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/document_model.dart';

class ApiService {
  // Use http://10.0.2.2:5000 for Android Emulator, http://localhost:5000 for iOS simulator/Web
  static const String baseUrl = 'http://10.0.2.2:5000'; 
  
  static String? _token;

  static Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  static Future<String?> getToken() async {
    if (_token != null) return _token;
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('jwt_token');
    return _token;
  }

  static Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
  }

  static Future<Map<String, String>> _getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Auth
  static Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['token'] != null) {
          await _saveToken(data['token']);
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> register(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  // Documents
  static Future<List<DocumentModel>> listDocuments() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/api/docs/list'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List list = data['documents'] ?? [];
        return list.map((item) => DocumentModel.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  static Future<bool> deleteDocument(int docId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.delete(
        Uri.parse('$baseUrl/api/docs/delete/$docId'),
        headers: headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> generateDocument(String type, String title, String data, {List<File>? images}) async {
    try {
      final token = await getToken();
      final uri = Uri.parse('$baseUrl/api/docs/generate');
      
      var request = http.MultipartRequest('POST', uri);
      if (token != null) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      
      request.fields['type'] = type;
      request.fields['title'] = title;
      request.fields['data'] = data;
      
      if (images != null) {
        for (var image in images) {
          if (await image.exists()) {
            request.files.add(await http.MultipartFile.fromPath('images', image.path));
          }
        }
      }
      
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  // File Download
  static Future<List<int>?> downloadDocument(int docId) async {
    try {
      final token = await getToken();
      final response = await http.get(
        Uri.parse('$baseUrl/api/docs/download/$docId'),
        headers: {
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );
      if (response.statusCode == 200) {
        return response.bodyBytes;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // File Conversion
  static Future<List<int>?> convertFile(File file, String sourceExt, {String? targetFormat}) async {
    try {
      final token = await getToken();
      String endpoint = '';
      
      if (sourceExt == 'docx') {
        endpoint = '$baseUrl/api/convert/document';
      } else if (sourceExt == 'pdf') {
        endpoint = '$baseUrl/baseUrl/api/convert/pdf'; // Wait, let's make sure it is baseUrl + '/api/convert/pdf'
        endpoint = '$baseUrl/api/convert/pdf';
      } else {
        endpoint = '$baseUrl/api/convert/image';
      }

      var request = http.MultipartRequest('POST', Uri.parse(endpoint));
      if (token != null) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      
      request.files.add(await http.MultipartFile.fromPath('file', file.path));
      if (targetFormat != null) {
        request.fields['target_format'] = targetFormat;
      }

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return response.bodyBytes;
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }
}

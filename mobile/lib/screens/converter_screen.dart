import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';

class ConverterScreen extends StatefulWidget {
  const ConverterScreen({super.key});

  @override
  State<ConverterScreen> createState() => _ConverterScreenState();
}

class _ConverterScreenState extends State<ConverterScreen> {
  File? _selectedFile;
  String? _fileExtension;
  String? _targetFormat;
  List<String> _availableFormats = [];
  bool _isLoading = false;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['docx', 'pdf', 'png', 'jpg', 'jpeg', 'jfif'],
    );

    if (result != null && result.files.single.path != null) {
      final file = File(result.files.single.path!);
      final ext = result.files.single.extension?.toLowerCase() ?? '';
      
      setState(() {
        _selectedFile = file;
        _fileExtension = ext;
        _targetFormat = null;
        _availableFormats = [];

        if (ext == 'docx') {
          _availableFormats = ['pdf'];
          _targetFormat = 'pdf';
        } else if (ext == 'pdf') {
          _availableFormats = ['pdfa'];
          _targetFormat = 'pdfa';
        } else if (['png', 'jpg', 'jpeg', 'jfif'].contains(ext)) {
          _availableFormats = ['png', 'jpg', 'jfif']
              .where((format) => format != ext && !(ext == 'jpeg' && format == 'jpg'))
              .toList();
          if (_availableFormats.isNotEmpty) {
            _targetFormat = _availableFormats.first;
          }
        }
      });
    }
  }

  void _clearFile() {
    setState(() {
      _selectedFile = null;
      _fileExtension = null;
      _targetFormat = null;
      _availableFormats = [];
    });
  }

  Future<void> _convert() async {
    if (_selectedFile == null || _fileExtension == null) return;

    setState(() {
      _isLoading = true;
    });

    final bytes = await ApiService.convertFile(
      _selectedFile!,
      _fileExtension!,
      targetFormat: _targetFormat,
    );

    if (mounted) {
      setState(() {
        _isLoading = false;
      });

      if (bytes != null) {
        final outName = _selectedFile!.path.split(Platform.pathSeparator).last.split('.').first;
        final finalExt = _targetFormat ?? 'pdf';
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Conversão finalizada com sucesso! Arquivo "$outName.$finalExt" baixado (${bytes.length} bytes)'),
            backgroundColor: Colors.green,
          ),
        );
        _clearFile();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Falha ao converter arquivo. Verifique se o servidor está ativo.'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('Conversor de Arquivos', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: const Color(0xFF1E293B),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Colors.blueAccent),
                  SizedBox(height: 20),
                  Text(
                    'Convertendo seu arquivo...',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ],
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Conversor inteligente',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Suba arquivos e converta formatos em segundos.',
                    style: TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                  const SizedBox(height: 32),

                  // File Picker Dropzone
                  if (_selectedFile == null)
                    GestureDetector(
                      onTap: _pickFile,
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 60, horizontal: 20),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B).withOpacity(0.5),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFF334155), style: BorderStyle.solid),
                        ),
                        child: const Column(
                          children: [
                            Icon(Icons.cloud_upload_outlined, size: 64, color: Colors.blueAccent),
                            SizedBox(height: 16),
                            Text(
                              'Selecione um Arquivo',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            SizedBox(height: 8),
                            Text(
                              'Formatos aceitos: DOCX, PNG, JPG, JFIF, PDF',
                              style: TextStyle(color: Colors.grey, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    // File Selected Info Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.insert_drive_file, color: Colors.blueAccent, size: 40),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _selectedFile!.path.split(Platform.pathSeparator).last,
                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Formato original: ${_fileExtension?.toUpperCase()}',
                                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.close, color: Colors.redAccent),
                                onPressed: _clearFile,
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          
                          // Format Selector dropdown
                          if (_availableFormats.isNotEmpty) ...[
                            const Align(
                              alignment: Alignment.centerLeft,
                              child: Text(
                                'Converter para:',
                                style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              decoration: BoxDecoration(
                                color: const Color(0xFF0F172A),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFF334155)),
                              ),
                              child: DropdownButtonHideUnderline(
                                child: DropdownButton<String>(
                                  value: _targetFormat,
                                  dropdownColor: const Color(0xFF0F172A),
                                  style: const TextStyle(color: Colors.white),
                                  icon: const Icon(Icons.arrow_drop_down, color: Colors.blueAccent),
                                  isExpanded: true,
                                  items: _availableFormats.map((String value) {
                                    return DropdownMenuItem<String>(
                                      value: value,
                                      child: Text(value.toUpperCase()),
                                    );
                                  }).toList(),
                                  onChanged: (newValue) {
                                    setState(() {
                                      _targetFormat = newValue;
                                    });
                                  },
                                ),
                              ),
                            ),
                          ],
                          
                          const SizedBox(height: 24),
                          
                          // Convert button
                          ElevatedButton.icon(
                            onPressed: _convert,
                            style: ElevatedButton.styleFrom(
                              minimumSize: const Size.fromHeight(50),
                              backgroundColor: Colors.blueAccent,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            icon: const Icon(Icons.transform, color: Colors.white),
                            label: const Text(
                              'Converter e Baixar',
                              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
    );
  }
}

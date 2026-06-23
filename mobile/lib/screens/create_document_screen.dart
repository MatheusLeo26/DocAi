import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';

class CreateDocumentScreen extends StatefulWidget {
  final String docType; // 'resume', 'contract', 'report'

  const CreateDocumentScreen({super.key, required this.docType});

  @override
  State<CreateDocumentScreen> createState() => _CreateDocumentScreenState();
}

class _CreateDocumentScreenState extends State<CreateDocumentScreen> {
  final _titleController = TextEditingController();
  final _dataController = TextEditingController();
  final List<File> _selectedImages = [];
  bool _isLoading = false;
  String _selectedLanguage = 'pt';
  String _selectedTemplate = 'classic';

  Future<void> _pickImages() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: true,
    );

    if (result != null) {
      setState(() {
        _selectedImages.addAll(
          result.paths
              .where((path) => path != null)
              .map((path) => File(path!))
              .toList(),
        );
      });
    }
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImages.removeAt(index);
    });
  }

  @override
  void initState() {
    super.initState();
    final typeName = widget.docType == 'resume'
        ? 'Currículo'
        : widget.docType == 'contract'
            ? 'Contrato'
            : 'Relatório';
    _titleController.text = '$typeName ${DateTime.now().day}/${DateTime.now().month} ${DateTime.now().hour}:${DateTime.now().minute}';
  }

  Future<void> _generate() async {
    if (_titleController.text.trim().isEmpty || _dataController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preencha o título e as informações do documento.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    String finalDocType = widget.docType;
    if (widget.docType == 'resume') {
      if (_selectedTemplate == 'modern') {
        if (_selectedLanguage == 'en') finalDocType = 'resume_modern_en';
        else if (_selectedLanguage == 'es') finalDocType = 'resume_modern_es';
        else finalDocType = 'resume_modern';
      } else if (_selectedTemplate == 'minimalist') {
        if (_selectedLanguage == 'en') finalDocType = 'resume_minimalist_en';
        else if (_selectedLanguage == 'es') finalDocType = 'resume_minimalist_es';
        else finalDocType = 'resume_minimalist';
      } else {
        if (_selectedLanguage == 'en') finalDocType = 'resume_en';
        else if (_selectedLanguage == 'es') finalDocType = 'resume_es';
        else finalDocType = 'resume';
      }
    }

    final success = await ApiService.generateDocument(
      finalDocType,
      _titleController.text.trim(),
      _dataController.text.trim(),
      images: _selectedImages,
    );

    if (mounted) {
      setState(() {
        _isLoading = false;
      });

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Documento gerado com sucesso!')),
        );
        Navigator.of(context).pop();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Erro ao gerar documento no servidor.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final titleLabel = widget.docType == 'resume'
        ? 'Gerar Currículo'
        : widget.docType == 'contract'
            ? 'Gerar Contrato'
            : 'Gerar Relatório';

    final hintText = widget.docType == 'resume'
        ? 'Insira suas informações profissionais (experiências, habilidades, formação)...'
        : widget.docType == 'contract'
            ? 'Descreva o acordo (partes contratantes, valor, objeto, data, etc)...'
            : 'Descreva os dados do relatório, fatos observados, tabelas e conclusões...';

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: Text(titleLabel, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
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
                    'Gerando seu documento com IA...',
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
                    'Configurações do Documento',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 16),
                  
                  if (widget.docType == 'resume') ...[
                    const Text(
                      'Idioma do Currículo',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        border: Border.all(color: const Color(0xFF334155)),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedLanguage,
                          dropdownColor: const Color(0xFF1E293B),
                          isExpanded: true,
                          icon: const Icon(Icons.arrow_drop_down, color: Colors.white),
                          style: const TextStyle(color: Colors.white),
                          onChanged: (String? newValue) {
                            setState(() {
                              _selectedLanguage = newValue!;
                            });
                          },
                          items: const [
                            DropdownMenuItem(value: 'pt', child: Text('Português')),
                            DropdownMenuItem(value: 'en', child: Text('English')),
                            DropdownMenuItem(value: 'es', child: Text('Español')),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Modelo de Currículo',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 180,
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            _buildTemplateCard('classic', 'Clássico', 'Inter & Azul', 'classic_preview.png'),
                            const SizedBox(width: 12),
                            _buildTemplateCard('modern', 'Moderno', 'Poppins & Verde', 'modern_preview.png'),
                            const SizedBox(width: 12),
                            _buildTemplateCard('minimalist', 'Minimalista', 'Serif, sem ícones', 'minimalist_preview.png'),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Title Input
                  TextField(
                    controller: _titleController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: 'Título do Documento',
                      labelStyle: const TextStyle(color: Colors.grey),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Color(0xFF334155)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Colors.blueAccent),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  
                  // Content Info Data Input
                  const Text(
                    'Informações para Alimentar a IA',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _dataController,
                    maxLines: 10,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: hintText,
                      hintStyle: const TextStyle(color: Colors.grey, fontSize: 14),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Color(0xFF334155)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: const BorderSide(color: Colors.blueAccent),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Image Attachments section
                  const Text(
                    'Anexos / Imagens complementares',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  if (_selectedImages.isNotEmpty) ...[
                    Container(
                      height: 100,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _selectedImages.length,
                        itemBuilder: (context, index) {
                          final file = _selectedImages[index];
                          return Stack(
                            children: [
                              Container(
                                margin: const EdgeInsets.only(right: 8),
                                width: 100,
                                height: 100,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: const Color(0xFF334155)),
                                  image: DecorationImage(
                                    image: FileImage(file),
                                    fit: BoxFit.cover,
                                  ),
                                ),
                              ),
                              Positioned(
                                top: 4,
                                right: 12,
                                child: GestureDetector(
                                  onTap: () => _removeImage(index),
                                  child: Container(
                                    padding: const EdgeInsets.all(4),
                                    decoration: const BoxDecoration(
                                      color: Colors.redAccent,
                                      shape: BoxShape.circle,
                                    ),
                                    child: const Icon(Icons.close, size: 16, color: Colors.white),
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  OutlinedButton.icon(
                    onPressed: _pickImages,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      side: const BorderSide(color: Color(0xFF334155)),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    icon: const Icon(Icons.add_a_photo, color: Colors.blueAccent),
                    label: const Text(
                      'Adicionar Imagem',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  // Generate Button
                  ElevatedButton.icon(
                    onPressed: _generate,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.blueAccent,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    icon: const Icon(Icons.rocket_launch, color: Colors.white),
                    label: const Text(
                      'Gerar e Salvar PDF',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildTemplateCard(String value, String title, String desc, String imageName) {
    final isSelected = _selectedTemplate == value;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedTemplate = value;
        });
      },
      child: Container(
        width: 140,
        decoration: BoxDecoration(
          color: isSelected ? Colors.blueAccent.withOpacity(0.1) : const Color(0xFF1E293B),
          border: Border.all(
            color: isSelected ? Colors.blueAccent : const Color(0xFF334155),
            width: 2,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  '${ApiService.baseUrl}/static/images/$imageName',
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Container(
                    color: const Color(0xFF334155),
                    child: const Icon(Icons.description, color: Colors.grey),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 12),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 2),
            Text(
              desc,
              style: const TextStyle(color: Colors.grey, fontSize: 10),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

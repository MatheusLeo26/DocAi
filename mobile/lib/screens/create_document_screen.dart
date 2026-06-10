import 'package:flutter/material.dart';
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
  bool _isLoading = false;

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

    final success = await ApiService.generateDocument(
      widget.docType,
      _titleController.text.trim(),
      _dataController.text.trim(),
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
}

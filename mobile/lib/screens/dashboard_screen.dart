import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'create_document_screen.dart';
import 'converter_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<DocumentModel> _documents = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchDocuments();
  }

  Future<void> _fetchDocuments() async {
    setState(() {
      _isLoading = true;
    });
    final docs = await ApiService.listDocuments();
    setState(() {
      _documents = docs;
      _isLoading = false;
    });
  }

  Future<void> _deleteDoc(int id) async {
    final success = await ApiService.deleteDocument(id);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Documento excluído com sucesso')),
      );
      _fetchDocuments();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Erro ao excluir documento')),
      );
    }
  }

  Future<void> _downloadDoc(int id, String title) async {
    final bytes = await ApiService.downloadDocument(id);
    if (bytes != null) {
      // In a real mobile app, you would save it using path_provider and open it.
      // Here we just notify the user.
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Download concluído para "$title" (${bytes.length} bytes)')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Erro ao baixar documento')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('Biblioteca', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: const Color(0xFF1E293B),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.blueAccent),
            onPressed: _fetchDocuments,
          )
        ],
      ),
      // Retractable Menu (Navigation Drawer)
      drawer: Drawer(
        backgroundColor: const Color(0xFF1E293B),
        child: Column(
          children: [
            const DrawerHeader(
              decoration: BoxDecoration(
                color: Color(0xFF0F172A),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'DocAI',
                      style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Documentos inteligentes',
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.library_books, color: Colors.blueAccent),
              title: const Text('Biblioteca', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.of(context).pop(); // Close drawer
              },
            ),
            ListTile(
              leading: const Icon(Icons.description, color: Colors.blueAccent),
              title: const Text('Criar Currículo', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const CreateDocumentScreen(docType: 'resume')),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.gavel, color: Colors.blueAccent),
              title: const Text('Criar Contrato', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const CreateDocumentScreen(docType: 'contract')),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.assessment, color: Colors.blueAccent),
              title: const Text('Criar Relatório', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const CreateDocumentScreen(docType: 'report')),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.transform, color: Colors.blueAccent),
              title: const Text('Conversor de Arquivos', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const ConverterScreen()),
                );
              },
            ),
            const Spacer(),
            const Divider(color: Color(0xFF334155)),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.redAccent),
              title: const Text('Sair', style: TextStyle(color: Colors.white)),
              onTap: () async {
                await ApiService.logout();
                if (mounted) {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                }
              },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.blueAccent))
          : _documents.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.folder_open, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      const Text(
                        'Nenhum documento gerado ainda.',
                        style: TextStyle(color: Colors.white, fontSize: 16),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const CreateDocumentScreen(docType: 'resume')),
                          );
                        },
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                        child: const Text('Criar Meu Primeiro Documento', style: TextStyle(color: Colors.white)),
                      )
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _documents.length,
                  itemBuilder: (context, index) {
                    final doc = _documents[index];
                    return Card(
                      color: const Color(0xFF1E293B),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: const BorderSide(color: Color(0xFF334155)),
                      ),
                      margin: const EdgeInsets.bottom(12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.blueAccent.withOpacity(0.2),
                          child: Icon(
                            doc.type.startsWith('resume')
                                ? Icons.description
                                : doc.type == 'contract'
                                    ? Icons.gavel
                                    : Icons.assessment,
                            color: Colors.blueAccent,
                          ),
                        ),
                        title: Text(
                          doc.title,
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          'Criado em: ${doc.createdAt.day}/${doc.createdAt.month}/${doc.createdAt.year}',
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.download, color: Colors.blueAccent),
                              onPressed: () => _downloadDoc(doc.id, doc.title),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.redAccent),
                              onPressed: () => _deleteDoc(doc.id),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}

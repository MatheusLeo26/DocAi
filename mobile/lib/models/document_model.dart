class DocumentModel {
  final int id;
  final String type;
  final String title;
  final DateTime createdAt;

  DocumentModel({
    required this.id,
    required this.type,
    required this.title,
    required this.createdAt,
  });

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    return DocumentModel(
      id: json['id'],
      type: json['type'],
      title: json['title'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

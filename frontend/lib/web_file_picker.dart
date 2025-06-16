// lib/web_file_picker.dart
// Wrapper para seleção de arquivo na Web usando dart:html

import 'dart:async';
import 'dart:html' as html;

/// Abre o dialog nativo de seleção de arquivo na Web e retorna o primeiro arquivo escolhido.
Future<html.File?> pickWebFile({List<String>? accept}) async {
  final completer = Completer<html.File?>();
  final input = html.FileUploadInputElement()
    ..accept = accept?.join(',') ?? 'image/*'
    ..click();

  input.onChange.listen((_) {
    final files = input.files;
    if (files != null && files.isNotEmpty) {
      completer.complete(files.first);
    } else {
      completer.complete(null);
    }
  });

  return completer.future;
}

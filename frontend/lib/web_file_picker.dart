// lib/web_file_picker.dart

import 'dart:html' as html;
import 'dart:async';

Future<html.File?> pickWebFile({List<String>? accept}) async {
  final completer = Completer<html.File?>();
  final uploadInput = html.FileUploadInputElement();
  if (accept != null) {
    uploadInput.accept = accept.join(',');
  }

  uploadInput.click();

  uploadInput.onChange.listen((event) {
    final files = uploadInput.files;
    if (files == null || files.isEmpty) {
      completer.complete(null);
    } else {
      completer.complete(files.first);
    }
  });

  return completer.future;
}

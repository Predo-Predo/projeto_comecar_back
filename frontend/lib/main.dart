import 'package:flutter/material.dart';
import 'login_page.dart';
import 'formulario_app_empresa.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Demo Frontend',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.teal,
        inputDecorationTheme: const InputDecorationTheme(
          border: UnderlineInputBorder(),
        ),
      ),
      // Rotas nomeadas
      routes: {
        '/': (ctx) => const LoginPage(),
        '/formulario_app': (ctx) {
          final companyId = ModalRoute.of(ctx)!.settings.arguments as int;
          return FormularioAppEmpresa(companyId: companyId);
        },
      },
      initialRoute: '/',
    );
  }
}

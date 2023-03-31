import 'package:app/components/style_transfer_form.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Pastiche',
      theme: ThemeData.dark(),
      home: const StyleTransferForm(),
    );
  }
}

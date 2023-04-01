import 'package:flutter/material.dart';

class OutputSection extends StatelessWidget {
  const OutputSection({
    super.key,
    required bool isLoading,
    required Image? resultImage,
  })  : _isLoading = isLoading,
        _resultImage = resultImage;

  final bool _isLoading;
  final Image? _resultImage;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 384.0,
      width: 384.0,
      child: Center(
        child: _isLoading
            ? const CircularProgressIndicator(
                color: Colors.white,
              )
            : _resultImage ??
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Colors.white,
                      width: 2.0,
                    ),
                  ),
                ),
      ),
    );
  }
}

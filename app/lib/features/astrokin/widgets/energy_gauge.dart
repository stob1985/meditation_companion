import 'package:flutter/material.dart';
import '../models/models.dart';
import '../theme/astrokin_theme.dart';

class EnergyGauge extends StatelessWidget {
  final FamilyEnergySnapshot? energy;
  final double size;

  const EnergyGauge({
    super.key,
    this.energy,
    this.size = 200,
  });

  @override
  Widget build(BuildContext context) {
    final value = energy?.overallEnergy ?? 0.5;
    final type = energy?.overallType ?? EnergyType.medium;

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.grey.shade200,
            ),
          ),
          // Progress indicator
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: value,
              strokeWidth: 12,
              backgroundColor: Colors.grey.shade300,
              valueColor: AlwaysStoppedAnimation(_getColor(type)),
            ),
          ),
          // Center content
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${(value * 100).round()}%',
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: _getColor(type),
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                _getLabel(type),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AstroKinTheme.textSecondary,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getColor(EnergyType type) {
    switch (type) {
      case EnergyType.high:
        return AstroKinTheme.energyHigh;
      case EnergyType.medium:
        return AstroKinTheme.energyMedium;
      case EnergyType.low:
        return AstroKinTheme.energyLow;
    }
  }

  String _getLabel(EnergyType type) {
    switch (type) {
      case EnergyType.high:
        return 'High Energy';
      case EnergyType.medium:
        return 'Balanced';
      case EnergyType.low:
        return 'Low Energy';
    }
  }
}

class EnergyBar extends StatelessWidget {
  final String label;
  final double value;
  final Color? color;

  const EnergyBar({
    super.key,
    required this.label,
    required this.value,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final barColor = color ?? _getColorForValue(value);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            Text(
              '${(value * 100).round()}%',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: barColor,
                  ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation(barColor),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Color _getColorForValue(double value) {
    if (value > 0.66) return AstroKinTheme.energyHigh;
    if (value > 0.33) return AstroKinTheme.energyMedium;
    return AstroKinTheme.energyLow;
  }
}

class CategoryEnergyGrid extends StatelessWidget {
  final Map<EnergyCategory, double> categories;

  const CategoryEnergyGrid({
    super.key,
    required this.categories,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: categories.entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
          child: EnergyBar(
            label: _getCategoryLabel(entry.key),
            value: entry.value,
            color: _getCategoryColor(entry.key),
          ),
        );
      }).toList(),
    );
  }

  String _getCategoryLabel(EnergyCategory category) {
    switch (category) {
      case EnergyCategory.emotional:
        return 'Emotional';
      case EnergyCategory.physical:
        return 'Physical';
      case EnergyCategory.mental:
        return 'Mental';
      case EnergyCategory.spiritual:
        return 'Spiritual';
    }
  }

  Color _getCategoryColor(EnergyCategory category) {
    switch (category) {
      case EnergyCategory.emotional:
        return AstroKinTheme.accentCoral;
      case EnergyCategory.physical:
        return AstroKinTheme.primaryGreen;
      case EnergyCategory.mental:
        return AstroKinTheme.primaryBlue;
      case EnergyCategory.spiritual:
        return AstroKinTheme.primaryPurple;
    }
  }
}

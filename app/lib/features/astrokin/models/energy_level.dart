import 'package:equatable/equatable.dart';

enum EnergyType {
  high,
  medium,
  low,
}

enum EnergyCategory {
  emotional,
  physical,
  mental,
  spiritual,
}

class EnergyLevel extends Equatable {
  final String id;
  final DateTime date;
  final EnergyType type;
  final EnergyCategory category;
  final double value; // 0.0 to 1.0
  final String? description;
  final List<String> recommendations;

  const EnergyLevel({
    required this.id,
    required this.date,
    required this.type,
    required this.category,
    required this.value,
    this.description,
    this.recommendations = const [],
  });

  EnergyLevel copyWith({
    String? id,
    DateTime? date,
    EnergyType? type,
    EnergyCategory? category,
    double? value,
    String? description,
    List<String>? recommendations,
  }) {
    return EnergyLevel(
      id: id ?? this.id,
      date: date ?? this.date,
      type: type ?? this.type,
      category: category ?? this.category,
      value: value ?? this.value,
      description: description ?? this.description,
      recommendations: recommendations ?? this.recommendations,
    );
  }

  String get typeDisplayName {
    switch (type) {
      case EnergyType.high:
        return 'High Energy';
      case EnergyType.medium:
        return 'Medium Energy';
      case EnergyType.low:
        return 'Low Energy';
    }
  }

  String get categoryDisplayName {
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

  int get colorValue {
    switch (type) {
      case EnergyType.high:
        return 0xFF4CAF50; // Green
      case EnergyType.medium:
        return 0xFFFFC107; // Amber
      case EnergyType.low:
        return 0xFFFF5722; // Deep Orange
    }
  }

  @override
  List<Object?> get props => [id, date, type, category, value, description, recommendations];
}

class FamilyEnergySnapshot extends Equatable {
  final DateTime date;
  final double overallEnergy; // 0.0 to 1.0
  final EnergyType overallType;
  final Map<EnergyCategory, double> categoryBreakdown;
  final List<String> insights;
  final List<String> recommendations;

  const FamilyEnergySnapshot({
    required this.date,
    required this.overallEnergy,
    required this.overallType,
    required this.categoryBreakdown,
    this.insights = const [],
    this.recommendations = const [],
  });

  factory FamilyEnergySnapshot.calculate({
    required DateTime date,
    required List<EnergyLevel> memberEnergies,
  }) {
    if (memberEnergies.isEmpty) {
      return FamilyEnergySnapshot(
        date: date,
        overallEnergy: 0.5,
        overallType: EnergyType.medium,
        categoryBreakdown: const {},
      );
    }

    final totalValue = memberEnergies.fold<double>(
      0,
      (sum, e) => sum + e.value,
    );
    final avgEnergy = totalValue / memberEnergies.length;

    final categoryBreakdown = <EnergyCategory, double>{};
    for (final category in EnergyCategory.values) {
      final categoryEnergies = memberEnergies.where((e) => e.category == category);
      if (categoryEnergies.isNotEmpty) {
        final categoryTotal = categoryEnergies.fold<double>(0, (sum, e) => sum + e.value);
        categoryBreakdown[category] = categoryTotal / categoryEnergies.length;
      }
    }

    final type = avgEnergy > 0.66
        ? EnergyType.high
        : avgEnergy > 0.33
            ? EnergyType.medium
            : EnergyType.low;

    return FamilyEnergySnapshot(
      date: date,
      overallEnergy: avgEnergy,
      overallType: type,
      categoryBreakdown: categoryBreakdown,
    );
  }

  @override
  List<Object?> get props => [date, overallEnergy, overallType, categoryBreakdown, insights, recommendations];
}

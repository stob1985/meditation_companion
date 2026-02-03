import 'package:equatable/equatable.dart';

enum EventType {
  newMoon,
  fullMoon,
  mercuryRetrograde,
  venusRetrograde,
  marsRetrograde,
  eclipse,
  conjunction,
  opposition,
  trine,
  square,
  seasonChange,
}

enum EventImpact {
  positive,
  neutral,
  challenging,
}

class AstrologicalEvent extends Equatable {
  final String id;
  final String name;
  final String description;
  final EventType type;
  final EventImpact impact;
  final DateTime startDate;
  final DateTime? endDate;
  final List<String> affectedSigns;
  final List<String> tips;
  final double intensity; // 0.0 to 1.0

  const AstrologicalEvent({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.impact,
    required this.startDate,
    this.endDate,
    this.affectedSigns = const [],
    this.tips = const [],
    this.intensity = 0.5,
  });

  AstrologicalEvent copyWith({
    String? id,
    String? name,
    String? description,
    EventType? type,
    EventImpact? impact,
    DateTime? startDate,
    DateTime? endDate,
    List<String>? affectedSigns,
    List<String>? tips,
    double? intensity,
  }) {
    return AstrologicalEvent(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      type: type ?? this.type,
      impact: impact ?? this.impact,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      affectedSigns: affectedSigns ?? this.affectedSigns,
      tips: tips ?? this.tips,
      intensity: intensity ?? this.intensity,
    );
  }

  bool get isRetrograde =>
      type == EventType.mercuryRetrograde ||
      type == EventType.venusRetrograde ||
      type == EventType.marsRetrograde;

  bool get isOngoing {
    final now = DateTime.now();
    if (endDate == null) {
      return now.year == startDate.year &&
          now.month == startDate.month &&
          now.day == startDate.day;
    }
    return now.isAfter(startDate) && now.isBefore(endDate!);
  }

  bool isActiveOn(DateTime date) {
    if (endDate == null) {
      return date.year == startDate.year &&
          date.month == startDate.month &&
          date.day == startDate.day;
    }
    return (date.isAfter(startDate) || date.isAtSameMomentAs(startDate)) &&
        (date.isBefore(endDate!) || date.isAtSameMomentAs(endDate!));
  }

  int get durationInDays {
    if (endDate == null) return 1;
    return endDate!.difference(startDate).inDays + 1;
  }

  String get typeDisplayName {
    switch (type) {
      case EventType.newMoon:
        return 'New Moon';
      case EventType.fullMoon:
        return 'Full Moon';
      case EventType.mercuryRetrograde:
        return 'Mercury Retrograde';
      case EventType.venusRetrograde:
        return 'Venus Retrograde';
      case EventType.marsRetrograde:
        return 'Mars Retrograde';
      case EventType.eclipse:
        return 'Eclipse';
      case EventType.conjunction:
        return 'Conjunction';
      case EventType.opposition:
        return 'Opposition';
      case EventType.trine:
        return 'Trine';
      case EventType.square:
        return 'Square';
      case EventType.seasonChange:
        return 'Season Change';
    }
  }

  String get impactEmoji {
    switch (impact) {
      case EventImpact.positive:
        return '✨';
      case EventImpact.neutral:
        return '🌙';
      case EventImpact.challenging:
        return '⚡';
    }
  }

  String get typeIcon {
    switch (type) {
      case EventType.newMoon:
        return '🌑';
      case EventType.fullMoon:
        return '🌕';
      case EventType.mercuryRetrograde:
        return '☿️';
      case EventType.venusRetrograde:
        return '♀️';
      case EventType.marsRetrograde:
        return '♂️';
      case EventType.eclipse:
        return '🌒';
      case EventType.conjunction:
        return '☌';
      case EventType.opposition:
        return '☍';
      case EventType.trine:
        return '△';
      case EventType.square:
        return '□';
      case EventType.seasonChange:
        return '🌿';
    }
  }

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        type,
        impact,
        startDate,
        endDate,
        affectedSigns,
        tips,
        intensity,
      ];
}

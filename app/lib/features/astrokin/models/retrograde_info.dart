import 'package:equatable/equatable.dart';
import 'astrological_event.dart';

enum RetrogradePlanet {
  mercury,
  venus,
  mars,
  jupiter,
  saturn,
}

class RetrogradeInfo extends Equatable {
  final String id;
  final RetrogradePlanet planet;
  final DateTime startDate;
  final DateTime endDate;
  final String description;
  final List<String> doList;
  final List<String> dontList;
  final List<String> familyTips;
  final List<String> communicationTips;
  final double intensity; // 0.0 to 1.0

  const RetrogradeInfo({
    required this.id,
    required this.planet,
    required this.startDate,
    required this.endDate,
    required this.description,
    this.doList = const [],
    this.dontList = const [],
    this.familyTips = const [],
    this.communicationTips = const [],
    this.intensity = 0.5,
  });

  RetrogradeInfo copyWith({
    String? id,
    RetrogradePlanet? planet,
    DateTime? startDate,
    DateTime? endDate,
    String? description,
    List<String>? doList,
    List<String>? dontList,
    List<String>? familyTips,
    List<String>? communicationTips,
    double? intensity,
  }) {
    return RetrogradeInfo(
      id: id ?? this.id,
      planet: planet ?? this.planet,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      description: description ?? this.description,
      doList: doList ?? this.doList,
      dontList: dontList ?? this.dontList,
      familyTips: familyTips ?? this.familyTips,
      communicationTips: communicationTips ?? this.communicationTips,
      intensity: intensity ?? this.intensity,
    );
  }

  bool get isActive {
    final now = DateTime.now();
    return now.isAfter(startDate) && now.isBefore(endDate);
  }

  int get daysRemaining {
    if (!isActive) return 0;
    return endDate.difference(DateTime.now()).inDays;
  }

  int get totalDays => endDate.difference(startDate).inDays;

  double get progress {
    if (!isActive) return isUpcoming ? 0.0 : 1.0;
    final elapsed = DateTime.now().difference(startDate).inDays;
    return elapsed / totalDays;
  }

  bool get isUpcoming {
    return DateTime.now().isBefore(startDate);
  }

  int get daysUntilStart {
    if (!isUpcoming) return 0;
    return startDate.difference(DateTime.now()).inDays;
  }

  String get planetName {
    switch (planet) {
      case RetrogradePlanet.mercury:
        return 'Mercury';
      case RetrogradePlanet.venus:
        return 'Venus';
      case RetrogradePlanet.mars:
        return 'Mars';
      case RetrogradePlanet.jupiter:
        return 'Jupiter';
      case RetrogradePlanet.saturn:
        return 'Saturn';
    }
  }

  String get planetSymbol {
    switch (planet) {
      case RetrogradePlanet.mercury:
        return '☿';
      case RetrogradePlanet.venus:
        return '♀';
      case RetrogradePlanet.mars:
        return '♂';
      case RetrogradePlanet.jupiter:
        return '♃';
      case RetrogradePlanet.saturn:
        return '♄';
    }
  }

  String get affectedArea {
    switch (planet) {
      case RetrogradePlanet.mercury:
        return 'Communication, Technology, Travel';
      case RetrogradePlanet.venus:
        return 'Love, Relationships, Values';
      case RetrogradePlanet.mars:
        return 'Energy, Motivation, Conflict';
      case RetrogradePlanet.jupiter:
        return 'Growth, Expansion, Luck';
      case RetrogradePlanet.saturn:
        return 'Structure, Discipline, Responsibility';
    }
  }

  AstrologicalEvent toEvent() {
    EventType eventType;
    switch (planet) {
      case RetrogradePlanet.mercury:
        eventType = EventType.mercuryRetrograde;
        break;
      case RetrogradePlanet.venus:
        eventType = EventType.venusRetrograde;
        break;
      case RetrogradePlanet.mars:
        eventType = EventType.marsRetrograde;
        break;
      default:
        eventType = EventType.mercuryRetrograde;
    }

    return AstrologicalEvent(
      id: id,
      name: '$planetName Retrograde',
      description: description,
      type: eventType,
      impact: EventImpact.challenging,
      startDate: startDate,
      endDate: endDate,
      tips: [...doList, ...familyTips],
      intensity: intensity,
    );
  }

  @override
  List<Object?> get props => [
        id,
        planet,
        startDate,
        endDate,
        description,
        doList,
        dontList,
        familyTips,
        communicationTips,
        intensity,
      ];
}

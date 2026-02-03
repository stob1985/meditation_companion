import 'package:equatable/equatable.dart';
import 'family_member.dart';
import 'zodiac_sign.dart';

enum HackCategory {
  behavior,
  emotions,
  learning,
  sleep,
  communication,
  creativity,
  socialSkills,
  energy,
}

class ParentingHack extends Equatable {
  final String id;
  final String title;
  final String description;
  final HackCategory category;
  final List<ZodiacSignType> targetSigns;
  final List<String> actionItems;
  final String? explanation;
  final DateTime? validFrom;
  final DateTime? validUntil;
  final double relevanceScore; // 0.0 to 1.0

  const ParentingHack({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    this.targetSigns = const [],
    this.actionItems = const [],
    this.explanation,
    this.validFrom,
    this.validUntil,
    this.relevanceScore = 0.5,
  });

  ParentingHack copyWith({
    String? id,
    String? title,
    String? description,
    HackCategory? category,
    List<ZodiacSignType>? targetSigns,
    List<String>? actionItems,
    String? explanation,
    DateTime? validFrom,
    DateTime? validUntil,
    double? relevanceScore,
  }) {
    return ParentingHack(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      targetSigns: targetSigns ?? this.targetSigns,
      actionItems: actionItems ?? this.actionItems,
      explanation: explanation ?? this.explanation,
      validFrom: validFrom ?? this.validFrom,
      validUntil: validUntil ?? this.validUntil,
      relevanceScore: relevanceScore ?? this.relevanceScore,
    );
  }

  bool isRelevantFor(FamilyMember child) {
    if (targetSigns.isEmpty) return true;
    return targetSigns.contains(child.zodiacSign.type);
  }

  bool get isCurrentlyValid {
    final now = DateTime.now();
    if (validFrom != null && now.isBefore(validFrom!)) return false;
    if (validUntil != null && now.isAfter(validUntil!)) return false;
    return true;
  }

  String get categoryDisplayName {
    switch (category) {
      case HackCategory.behavior:
        return 'Behavior';
      case HackCategory.emotions:
        return 'Emotions';
      case HackCategory.learning:
        return 'Learning';
      case HackCategory.sleep:
        return 'Sleep';
      case HackCategory.communication:
        return 'Communication';
      case HackCategory.creativity:
        return 'Creativity';
      case HackCategory.socialSkills:
        return 'Social Skills';
      case HackCategory.energy:
        return 'Energy';
    }
  }

  String get categoryIcon {
    switch (category) {
      case HackCategory.behavior:
        return '🎯';
      case HackCategory.emotions:
        return '💝';
      case HackCategory.learning:
        return '📚';
      case HackCategory.sleep:
        return '😴';
      case HackCategory.communication:
        return '💬';
      case HackCategory.creativity:
        return '🎨';
      case HackCategory.socialSkills:
        return '🤝';
      case HackCategory.energy:
        return '⚡';
    }
  }

  @override
  List<Object?> get props => [
        id,
        title,
        description,
        category,
        targetSigns,
        actionItems,
        explanation,
        validFrom,
        validUntil,
        relevanceScore,
      ];
}

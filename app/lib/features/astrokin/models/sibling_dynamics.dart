import 'package:equatable/equatable.dart';
import 'family_member.dart';
import 'zodiac_sign.dart';

enum DynamicType {
  harmonious,
  challenging,
  neutral,
  complementary,
}

enum RelationshipAspect {
  communication,
  playStyle,
  conflictResolution,
  sharedInterests,
  emotionalConnection,
}

class SiblingDynamic extends Equatable {
  final String id;
  final FamilyMember sibling1;
  final FamilyMember sibling2;
  final DynamicType overallDynamic;
  final double compatibilityScore; // 0.0 to 1.0
  final Map<RelationshipAspect, double> aspectScores;
  final List<String> strengths;
  final List<String> challenges;
  final List<String> tips;
  final String? currentPhaseInsight;

  const SiblingDynamic({
    required this.id,
    required this.sibling1,
    required this.sibling2,
    required this.overallDynamic,
    required this.compatibilityScore,
    this.aspectScores = const {},
    this.strengths = const [],
    this.challenges = const [],
    this.tips = const [],
    this.currentPhaseInsight,
  });

  factory SiblingDynamic.analyze({
    required String id,
    required FamilyMember sibling1,
    required FamilyMember sibling2,
  }) {
    final compatibility = _calculateElementCompatibility(
      sibling1.zodiacSign.element,
      sibling2.zodiacSign.element,
    );

    final dynamicType = compatibility > 0.7
        ? DynamicType.harmonious
        : compatibility > 0.5
            ? DynamicType.complementary
            : compatibility > 0.3
                ? DynamicType.neutral
                : DynamicType.challenging;

    final strengths = _getStrengths(sibling1.zodiacSign, sibling2.zodiacSign);
    final challenges = _getChallenges(sibling1.zodiacSign, sibling2.zodiacSign);
    final tips = _getTips(sibling1.zodiacSign, sibling2.zodiacSign, dynamicType);

    return SiblingDynamic(
      id: id,
      sibling1: sibling1,
      sibling2: sibling2,
      overallDynamic: dynamicType,
      compatibilityScore: compatibility,
      aspectScores: _calculateAspectScores(sibling1.zodiacSign, sibling2.zodiacSign),
      strengths: strengths,
      challenges: challenges,
      tips: tips,
    );
  }

  static double _calculateElementCompatibility(Element e1, Element e2) {
    if (e1 == e2) return 0.9;

    // Compatible elements
    if ((e1 == Element.fire && e2 == Element.air) ||
        (e1 == Element.air && e2 == Element.fire)) return 0.8;
    if ((e1 == Element.earth && e2 == Element.water) ||
        (e1 == Element.water && e2 == Element.earth)) return 0.8;

    // Neutral combinations
    if ((e1 == Element.fire && e2 == Element.earth) ||
        (e1 == Element.earth && e2 == Element.fire)) return 0.5;
    if ((e1 == Element.air && e2 == Element.water) ||
        (e1 == Element.water && e2 == Element.air)) return 0.5;

    // Challenging combinations
    if ((e1 == Element.fire && e2 == Element.water) ||
        (e1 == Element.water && e2 == Element.fire)) return 0.3;
    if ((e1 == Element.air && e2 == Element.earth) ||
        (e1 == Element.earth && e2 == Element.air)) return 0.4;

    return 0.5;
  }

  static Map<RelationshipAspect, double> _calculateAspectScores(
    ZodiacSign sign1,
    ZodiacSign sign2,
  ) {
    final baseScore = _calculateElementCompatibility(sign1.element, sign2.element);

    return {
      RelationshipAspect.communication: _adjustScore(baseScore, sign1.element == Element.air || sign2.element == Element.air ? 0.1 : 0),
      RelationshipAspect.playStyle: _adjustScore(baseScore, sign1.element == sign2.element ? 0.15 : 0),
      RelationshipAspect.conflictResolution: _adjustScore(baseScore, sign1.modality == sign2.modality ? -0.1 : 0.1),
      RelationshipAspect.sharedInterests: _adjustScore(baseScore, 0),
      RelationshipAspect.emotionalConnection: _adjustScore(baseScore, sign1.element == Element.water || sign2.element == Element.water ? 0.1 : 0),
    };
  }

  static double _adjustScore(double base, double adjustment) {
    return (base + adjustment).clamp(0.0, 1.0);
  }

  static List<String> _getStrengths(ZodiacSign sign1, ZodiacSign sign2) {
    final strengths = <String>[];

    if (sign1.element == sign2.element) {
      strengths.add('Natural understanding of each other\'s needs');
    }
    if (sign1.modality != sign2.modality) {
      strengths.add('Complementary approaches to tasks');
    }
    if ((sign1.element == Element.fire && sign2.element == Element.air) ||
        (sign1.element == Element.air && sign2.element == Element.fire)) {
      strengths.add('High energy and creative synergy');
    }
    if ((sign1.element == Element.earth && sign2.element == Element.water) ||
        (sign1.element == Element.water && sign2.element == Element.earth)) {
      strengths.add('Nurturing and supportive bond');
    }

    if (strengths.isEmpty) {
      strengths.add('Opportunity for growth through differences');
    }

    return strengths;
  }

  static List<String> _getChallenges(ZodiacSign sign1, ZodiacSign sign2) {
    final challenges = <String>[];

    if (sign1.modality == sign2.modality && sign1.modality == Modality.fixed) {
      challenges.add('Both may be stubborn during disagreements');
    }
    if (sign1.modality == sign2.modality && sign1.modality == Modality.cardinal) {
      challenges.add('Competition for leadership roles');
    }
    if ((sign1.element == Element.fire && sign2.element == Element.water) ||
        (sign1.element == Element.water && sign2.element == Element.fire)) {
      challenges.add('Different emotional expression styles');
    }
    if ((sign1.element == Element.air && sign2.element == Element.earth) ||
        (sign1.element == Element.earth && sign2.element == Element.air)) {
      challenges.add('Different pace and priorities');
    }

    if (challenges.isEmpty) {
      challenges.add('Minor adjustments needed for harmony');
    }

    return challenges;
  }

  static List<String> _getTips(ZodiacSign sign1, ZodiacSign sign2, DynamicType dynamic) {
    final tips = <String>[];

    switch (dynamic) {
      case DynamicType.harmonious:
        tips.add('Encourage collaborative projects to strengthen their bond');
        tips.add('Allow them to develop their own conflict resolution methods');
        break;
      case DynamicType.complementary:
        tips.add('Help them appreciate each other\'s unique strengths');
        tips.add('Create opportunities for them to teach each other');
        break;
      case DynamicType.neutral:
        tips.add('Find shared activities that appeal to both temperaments');
        tips.add('Be patient as they learn to understand each other');
        break;
      case DynamicType.challenging:
        tips.add('Establish clear boundaries and fair rules');
        tips.add('Schedule one-on-one time with each child');
        tips.add('Model healthy conflict resolution');
        break;
    }

    return tips;
  }

  String get dynamicDisplayName {
    switch (overallDynamic) {
      case DynamicType.harmonious:
        return 'Harmonious';
      case DynamicType.challenging:
        return 'Challenging';
      case DynamicType.neutral:
        return 'Neutral';
      case DynamicType.complementary:
        return 'Complementary';
    }
  }

  String get dynamicEmoji {
    switch (overallDynamic) {
      case DynamicType.harmonious:
        return '💚';
      case DynamicType.challenging:
        return '🔥';
      case DynamicType.neutral:
        return '🌙';
      case DynamicType.complementary:
        return '🤝';
    }
  }

  @override
  List<Object?> get props => [
        id,
        sibling1,
        sibling2,
        overallDynamic,
        compatibilityScore,
        aspectScores,
        strengths,
        challenges,
        tips,
        currentPhaseInsight,
      ];
}

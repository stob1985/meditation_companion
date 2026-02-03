import 'dart:math';
import '../models/models.dart';
import 'astrokin_repository.dart';

class MockAstroKinRepository implements AstroKinRepository {
  Family? _family;
  final _random = Random();

  // Pre-populated mock data
  final List<AstrologicalEvent> _mockEvents = [];
  final List<RetrogradeInfo> _mockRetrogrades = [];

  MockAstroKinRepository() {
    _initializeMockData();
  }

  void _initializeMockData() {
    final now = DateTime.now();

    // Initialize mock astrological events
    _mockEvents.addAll([
      AstrologicalEvent(
        id: 'event_1',
        name: 'New Moon in Aquarius',
        description: 'A time for new beginnings and innovative ideas. Perfect for family brainstorming sessions.',
        type: EventType.newMoon,
        impact: EventImpact.positive,
        startDate: now.add(const Duration(days: 2)),
        tips: [
          'Start new family projects together',
          'Have a family meeting to discuss goals',
          'Encourage creative expression in children',
        ],
        intensity: 0.7,
      ),
      AstrologicalEvent(
        id: 'event_2',
        name: 'Full Moon in Leo',
        description: 'Emotions run high. Children may seek more attention and validation.',
        type: EventType.fullMoon,
        impact: EventImpact.challenging,
        startDate: now.add(const Duration(days: 16)),
        tips: [
          'Plan special one-on-one time with each child',
          'Avoid scheduling important discussions',
          'Channel energy into creative activities',
        ],
        intensity: 0.8,
      ),
      AstrologicalEvent(
        id: 'event_3',
        name: 'Venus Trine Jupiter',
        description: 'Harmony and joy fill the home. Great time for family bonding.',
        type: EventType.trine,
        impact: EventImpact.positive,
        startDate: now.add(const Duration(days: 5)),
        endDate: now.add(const Duration(days: 7)),
        tips: [
          'Plan a family outing or celebration',
          'Express appreciation for each family member',
          'Start new traditions',
        ],
        intensity: 0.6,
      ),
      AstrologicalEvent(
        id: 'event_4',
        name: 'Mars Square Saturn',
        description: 'Frustrations may arise. Patience is key during this transit.',
        type: EventType.square,
        impact: EventImpact.challenging,
        startDate: now.add(const Duration(days: 10)),
        endDate: now.add(const Duration(days: 12)),
        tips: [
          'Avoid power struggles with children',
          'Take breaks when tensions rise',
          'Focus on individual tasks rather than group activities',
        ],
        intensity: 0.75,
      ),
    ]);

    // Initialize mock retrogrades
    _mockRetrogrades.addAll([
      RetrogradeInfo(
        id: 'retro_1',
        planet: RetrogradePlanet.mercury,
        startDate: now.subtract(const Duration(days: 5)),
        endDate: now.add(const Duration(days: 16)),
        description: 'Mercury retrograde affects communication and technology. Be patient with misunderstandings.',
        doList: [
          'Double-check all communications',
          'Back up important files',
          'Revisit unfinished projects',
          'Practice active listening with family',
        ],
        dontList: [
          'Make major purchases',
          'Sign important contracts',
          'Start new projects',
          'Assume you were understood',
        ],
        familyTips: [
          'Be extra patient with children\'s communication',
          'Review homework and school messages carefully',
          'Expect schedule changes and delays',
          'Use this time for family reflection',
        ],
        communicationTips: [
          'Repeat important information back',
          'Write down agreements',
          'Ask clarifying questions',
          'Be patient with technology glitches',
        ],
        intensity: 0.7,
      ),
      RetrogradeInfo(
        id: 'retro_2',
        planet: RetrogradePlanet.venus,
        startDate: now.add(const Duration(days: 45)),
        endDate: now.add(const Duration(days: 85)),
        description: 'Venus retrograde is a time to review relationships and values within the family.',
        doList: [
          'Reflect on family relationships',
          'Reconnect with extended family',
          'Reassess family budget and values',
          'Practice gratitude',
        ],
        dontList: [
          'Make drastic relationship decisions',
          'Overspend on luxuries',
          'Ignore relationship issues',
        ],
        familyTips: [
          'Have heart-to-heart conversations',
          'Review and appreciate what you have',
          'Work on unresolved family issues',
        ],
        communicationTips: [
          'Express love and appreciation',
          'Address old grievances gently',
          'Listen with empathy',
        ],
        intensity: 0.6,
      ),
    ]);
  }

  @override
  Future<Family?> getFamily() async {
    await Future.delayed(const Duration(milliseconds: 300));
    return _family;
  }

  @override
  Future<Family> createFamily(String name) async {
    await Future.delayed(const Duration(milliseconds: 500));
    _family = Family(
      id: 'family_${DateTime.now().millisecondsSinceEpoch}',
      name: name,
      members: [],
      createdAt: DateTime.now(),
    );
    return _family!;
  }

  @override
  Future<Family> updateFamily(Family family) async {
    await Future.delayed(const Duration(milliseconds: 300));
    _family = family.copyWith(updatedAt: DateTime.now());
    return _family!;
  }

  @override
  Future<void> deleteFamily(String familyId) async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_family?.id == familyId) {
      _family = null;
    }
  }

  @override
  Future<FamilyMember> addFamilyMember(FamilyMember member) async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_family == null) {
      throw Exception('No family exists. Create a family first.');
    }
    _family = _family!.addMember(member);
    return member;
  }

  @override
  Future<FamilyMember> updateFamilyMember(FamilyMember member) async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_family == null) {
      throw Exception('No family exists.');
    }
    _family = _family!.updateMember(member);
    return member;
  }

  @override
  Future<void> removeFamilyMember(String memberId) async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_family != null) {
      _family = _family!.removeMember(memberId);
    }
  }

  @override
  Future<FamilyEnergySnapshot> getFamilyEnergy(DateTime date) async {
    await Future.delayed(const Duration(milliseconds: 200));

    if (_family == null || _family!.members.isEmpty) {
      return FamilyEnergySnapshot(
        date: date,
        overallEnergy: 0.5,
        overallType: EnergyType.medium,
        categoryBreakdown: {},
        insights: ['Add family members to see energy insights'],
        recommendations: ['Start by adding family member profiles'],
      );
    }

    // Generate mock energy based on date and family composition
    final baseEnergy = 0.4 + (_random.nextDouble() * 0.4);
    final dayOfWeek = date.weekday;

    // Weekends tend to have different energy
    final weekendBonus = (dayOfWeek == 6 || dayOfWeek == 7) ? 0.1 : 0;
    final overallEnergy = (baseEnergy + weekendBonus).clamp(0.0, 1.0);

    final type = overallEnergy > 0.66
        ? EnergyType.high
        : overallEnergy > 0.33
            ? EnergyType.medium
            : EnergyType.low;

    return FamilyEnergySnapshot(
      date: date,
      overallEnergy: overallEnergy,
      overallType: type,
      categoryBreakdown: {
        EnergyCategory.emotional: 0.3 + (_random.nextDouble() * 0.5),
        EnergyCategory.physical: 0.4 + (_random.nextDouble() * 0.4),
        EnergyCategory.mental: 0.35 + (_random.nextDouble() * 0.45),
        EnergyCategory.spiritual: 0.5 + (_random.nextDouble() * 0.3),
      },
      insights: _generateInsights(type),
      recommendations: _generateRecommendations(type),
    );
  }

  List<String> _generateInsights(EnergyType type) {
    switch (type) {
      case EnergyType.high:
        return [
          'Family energy is vibrant today!',
          'Great day for group activities',
          'Children may have extra enthusiasm',
        ];
      case EnergyType.medium:
        return [
          'Balanced energy today',
          'Good for routine activities',
          'Mix of active and quiet time recommended',
        ];
      case EnergyType.low:
        return [
          'Energy levels are lower today',
          'Focus on rest and relaxation',
          'Avoid overscheduling activities',
        ];
    }
  }

  List<String> _generateRecommendations(EnergyType type) {
    switch (type) {
      case EnergyType.high:
        return [
          'Plan outdoor activities',
          'Tackle challenging projects together',
          'Channel energy into creative pursuits',
        ];
      case EnergyType.medium:
        return [
          'Maintain regular routines',
          'Balance active and quiet activities',
          'Good day for learning activities',
        ];
      case EnergyType.low:
        return [
          'Schedule quiet time',
          'Watch movies together',
          'Avoid demanding activities',
          'Practice calming exercises',
        ];
    }
  }

  @override
  Future<List<FamilyEnergySnapshot>> getEnergyHistory(DateTime start, DateTime end) async {
    await Future.delayed(const Duration(milliseconds: 400));

    final snapshots = <FamilyEnergySnapshot>[];
    var current = start;

    while (current.isBefore(end) || current.isAtSameMomentAs(end)) {
      snapshots.add(await getFamilyEnergy(current));
      current = current.add(const Duration(days: 1));
    }

    return snapshots;
  }

  @override
  Future<List<AstrologicalEvent>> getUpcomingEvents({int days = 30}) async {
    await Future.delayed(const Duration(milliseconds: 200));

    final now = DateTime.now();
    final endDate = now.add(Duration(days: days));

    return _mockEvents.where((event) {
      return event.startDate.isAfter(now) && event.startDate.isBefore(endDate);
    }).toList()
      ..sort((a, b) => a.startDate.compareTo(b.startDate));
  }

  @override
  Future<List<AstrologicalEvent>> getEventsForDate(DateTime date) async {
    await Future.delayed(const Duration(milliseconds: 150));

    return _mockEvents.where((event) => event.isActiveOn(date)).toList();
  }

  @override
  Future<List<ParentingHack>> getParentingHacks(FamilyMember child) async {
    await Future.delayed(const Duration(milliseconds: 300));

    return _generateHacksForSign(child.zodiacSign);
  }

  List<ParentingHack> _generateHacksForSign(ZodiacSign sign) {
    final hacks = <ParentingHack>[];

    // Element-based hacks
    switch (sign.element) {
      case Element.fire:
        hacks.addAll([
          ParentingHack(
            id: 'hack_fire_1',
            title: 'Channel Their Energy',
            description: 'Your fire sign child has abundant energy. Provide physical outlets to prevent restlessness.',
            category: HackCategory.energy,
            targetSigns: [ZodiacSignType.aries, ZodiacSignType.leo, ZodiacSignType.sagittarius],
            actionItems: [
              'Schedule daily physical activity',
              'Create adventure-based learning activities',
              'Allow leadership opportunities',
            ],
            explanation: 'Fire signs need movement and excitement to feel balanced.',
            relevanceScore: 0.9,
          ),
          ParentingHack(
            id: 'hack_fire_2',
            title: 'Encourage Independence',
            description: 'Fire signs thrive when given autonomy. Let them make age-appropriate decisions.',
            category: HackCategory.behavior,
            targetSigns: [ZodiacSignType.aries, ZodiacSignType.leo, ZodiacSignType.sagittarius],
            actionItems: [
              'Offer choices rather than commands',
              'Praise initiative and bravery',
              'Allow safe risk-taking',
            ],
            relevanceScore: 0.85,
          ),
        ]);
        break;
      case Element.earth:
        hacks.addAll([
          ParentingHack(
            id: 'hack_earth_1',
            title: 'Maintain Routines',
            description: 'Your earth sign child finds comfort in predictability. Consistent routines provide security.',
            category: HackCategory.behavior,
            targetSigns: [ZodiacSignType.taurus, ZodiacSignType.virgo, ZodiacSignType.capricorn],
            actionItems: [
              'Establish consistent daily schedules',
              'Give advance notice of changes',
              'Create visual routine charts',
            ],
            relevanceScore: 0.9,
          ),
          ParentingHack(
            id: 'hack_earth_2',
            title: 'Hands-On Learning',
            description: 'Earth signs learn best through touch and experience. Provide tactile learning opportunities.',
            category: HackCategory.learning,
            targetSigns: [ZodiacSignType.taurus, ZodiacSignType.virgo, ZodiacSignType.capricorn],
            actionItems: [
              'Use manipulatives for learning',
              'Garden or cook together',
              'Build and create with hands',
            ],
            relevanceScore: 0.85,
          ),
        ]);
        break;
      case Element.air:
        hacks.addAll([
          ParentingHack(
            id: 'hack_air_1',
            title: 'Encourage Communication',
            description: 'Your air sign child processes through talking. Create opportunities for verbal expression.',
            category: HackCategory.communication,
            targetSigns: [ZodiacSignType.gemini, ZodiacSignType.libra, ZodiacSignType.aquarius],
            actionItems: [
              'Have regular one-on-one conversations',
              'Ask open-ended questions',
              'Validate their ideas and thoughts',
            ],
            relevanceScore: 0.9,
          ),
          ParentingHack(
            id: 'hack_air_2',
            title: 'Provide Mental Stimulation',
            description: 'Air signs need mental engagement. Boredom leads to restlessness.',
            category: HackCategory.learning,
            targetSigns: [ZodiacSignType.gemini, ZodiacSignType.libra, ZodiacSignType.aquarius],
            actionItems: [
              'Introduce varied activities',
              'Encourage reading and puzzles',
              'Allow multiple interests',
            ],
            relevanceScore: 0.85,
          ),
        ]);
        break;
      case Element.water:
        hacks.addAll([
          ParentingHack(
            id: 'hack_water_1',
            title: 'Honor Their Emotions',
            description: 'Your water sign child feels deeply. Create a safe space for emotional expression.',
            category: HackCategory.emotions,
            targetSigns: [ZodiacSignType.cancer, ZodiacSignType.scorpio, ZodiacSignType.pisces],
            actionItems: [
              'Validate all feelings without judgment',
              'Teach emotional vocabulary',
              'Model healthy emotional expression',
            ],
            relevanceScore: 0.9,
          ),
          ParentingHack(
            id: 'hack_water_2',
            title: 'Provide Security',
            description: 'Water signs need emotional security. Consistent love and presence are essential.',
            category: HackCategory.emotions,
            targetSigns: [ZodiacSignType.cancer, ZodiacSignType.scorpio, ZodiacSignType.pisces],
            actionItems: [
              'Establish bedtime rituals',
              'Create cozy safe spaces',
              'Offer physical comfort often',
            ],
            relevanceScore: 0.85,
          ),
        ]);
        break;
    }

    return hacks;
  }

  @override
  Future<ParentingHack> getDailyHack(FamilyMember child) async {
    await Future.delayed(const Duration(milliseconds: 200));

    final hacks = _generateHacksForSign(child.zodiacSign);
    final dayIndex = DateTime.now().day % hacks.length;
    return hacks[dayIndex];
  }

  @override
  Future<List<SiblingDynamic>> getSiblingDynamics() async {
    await Future.delayed(const Duration(milliseconds: 300));

    if (_family == null) return [];

    final children = _family!.children;
    if (children.length < 2) return [];

    final dynamics = <SiblingDynamic>[];

    for (var i = 0; i < children.length - 1; i++) {
      for (var j = i + 1; j < children.length; j++) {
        dynamics.add(
          SiblingDynamic.analyze(
            id: 'dynamic_${children[i].id}_${children[j].id}',
            sibling1: children[i],
            sibling2: children[j],
          ),
        );
      }
    }

    return dynamics;
  }

  @override
  Future<SiblingDynamic> analyzeSiblings(FamilyMember sibling1, FamilyMember sibling2) async {
    await Future.delayed(const Duration(milliseconds: 300));

    return SiblingDynamic.analyze(
      id: 'dynamic_${sibling1.id}_${sibling2.id}',
      sibling1: sibling1,
      sibling2: sibling2,
    );
  }

  @override
  Future<List<RetrogradeInfo>> getActiveRetrogrades() async {
    await Future.delayed(const Duration(milliseconds: 200));

    return _mockRetrogrades.where((r) => r.isActive).toList();
  }

  @override
  Future<List<RetrogradeInfo>> getUpcomingRetrogrades({int days = 90}) async {
    await Future.delayed(const Duration(milliseconds: 200));

    final now = DateTime.now();
    final endDate = now.add(Duration(days: days));

    return _mockRetrogrades.where((r) {
      return r.startDate.isAfter(now) && r.startDate.isBefore(endDate);
    }).toList()
      ..sort((a, b) => a.startDate.compareTo(b.startDate));
  }

  @override
  Future<RetrogradeInfo?> getCurrentMercuryRetrograde() async {
    await Future.delayed(const Duration(milliseconds: 150));

    try {
      return _mockRetrogrades.firstWhere(
        (r) => r.planet == RetrogradePlanet.mercury && r.isActive,
      );
    } catch (_) {
      return null;
    }
  }
}

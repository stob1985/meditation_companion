import 'package:equatable/equatable.dart';

enum ZodiacSignType {
  aries,
  taurus,
  gemini,
  cancer,
  leo,
  virgo,
  libra,
  scorpio,
  sagittarius,
  capricorn,
  aquarius,
  pisces,
}

enum Element {
  fire,
  earth,
  air,
  water,
}

enum Modality {
  cardinal,
  fixed,
  mutable,
}

class ZodiacSign extends Equatable {
  final ZodiacSignType type;
  final String name;
  final String symbol;
  final Element element;
  final Modality modality;
  final String rulingPlanet;
  final DateTime startDate;
  final DateTime endDate;

  const ZodiacSign({
    required this.type,
    required this.name,
    required this.symbol,
    required this.element,
    required this.modality,
    required this.rulingPlanet,
    required this.startDate,
    required this.endDate,
  });

  static ZodiacSign fromDate(DateTime date) {
    final month = date.month;
    final day = date.day;

    if ((month == 3 && day >= 21) || (month == 4 && day <= 19)) {
      return zodiacSigns[ZodiacSignType.aries]!;
    } else if ((month == 4 && day >= 20) || (month == 5 && day <= 20)) {
      return zodiacSigns[ZodiacSignType.taurus]!;
    } else if ((month == 5 && day >= 21) || (month == 6 && day <= 20)) {
      return zodiacSigns[ZodiacSignType.gemini]!;
    } else if ((month == 6 && day >= 21) || (month == 7 && day <= 22)) {
      return zodiacSigns[ZodiacSignType.cancer]!;
    } else if ((month == 7 && day >= 23) || (month == 8 && day <= 22)) {
      return zodiacSigns[ZodiacSignType.leo]!;
    } else if ((month == 8 && day >= 23) || (month == 9 && day <= 22)) {
      return zodiacSigns[ZodiacSignType.virgo]!;
    } else if ((month == 9 && day >= 23) || (month == 10 && day <= 22)) {
      return zodiacSigns[ZodiacSignType.libra]!;
    } else if ((month == 10 && day >= 23) || (month == 11 && day <= 21)) {
      return zodiacSigns[ZodiacSignType.scorpio]!;
    } else if ((month == 11 && day >= 22) || (month == 12 && day <= 21)) {
      return zodiacSigns[ZodiacSignType.sagittarius]!;
    } else if ((month == 12 && day >= 22) || (month == 1 && day <= 19)) {
      return zodiacSigns[ZodiacSignType.capricorn]!;
    } else if ((month == 1 && day >= 20) || (month == 2 && day <= 18)) {
      return zodiacSigns[ZodiacSignType.aquarius]!;
    } else {
      return zodiacSigns[ZodiacSignType.pisces]!;
    }
  }

  String get elementEmoji {
    switch (element) {
      case Element.fire:
        return '🔥';
      case Element.earth:
        return '🌍';
      case Element.air:
        return '💨';
      case Element.water:
        return '💧';
    }
  }

  @override
  List<Object?> get props => [type, name, symbol, element, modality, rulingPlanet];
}

final Map<ZodiacSignType, ZodiacSign> zodiacSigns = {
  ZodiacSignType.aries: ZodiacSign(
    type: ZodiacSignType.aries,
    name: 'Aries',
    symbol: '♈',
    element: Element.fire,
    modality: Modality.cardinal,
    rulingPlanet: 'Mars',
    startDate: DateTime(2024, 3, 21),
    endDate: DateTime(2024, 4, 19),
  ),
  ZodiacSignType.taurus: ZodiacSign(
    type: ZodiacSignType.taurus,
    name: 'Taurus',
    symbol: '♉',
    element: Element.earth,
    modality: Modality.fixed,
    rulingPlanet: 'Venus',
    startDate: DateTime(2024, 4, 20),
    endDate: DateTime(2024, 5, 20),
  ),
  ZodiacSignType.gemini: ZodiacSign(
    type: ZodiacSignType.gemini,
    name: 'Gemini',
    symbol: '♊',
    element: Element.air,
    modality: Modality.mutable,
    rulingPlanet: 'Mercury',
    startDate: DateTime(2024, 5, 21),
    endDate: DateTime(2024, 6, 20),
  ),
  ZodiacSignType.cancer: ZodiacSign(
    type: ZodiacSignType.cancer,
    name: 'Cancer',
    symbol: '♋',
    element: Element.water,
    modality: Modality.cardinal,
    rulingPlanet: 'Moon',
    startDate: DateTime(2024, 6, 21),
    endDate: DateTime(2024, 7, 22),
  ),
  ZodiacSignType.leo: ZodiacSign(
    type: ZodiacSignType.leo,
    name: 'Leo',
    symbol: '♌',
    element: Element.fire,
    modality: Modality.fixed,
    rulingPlanet: 'Sun',
    startDate: DateTime(2024, 7, 23),
    endDate: DateTime(2024, 8, 22),
  ),
  ZodiacSignType.virgo: ZodiacSign(
    type: ZodiacSignType.virgo,
    name: 'Virgo',
    symbol: '♍',
    element: Element.earth,
    modality: Modality.mutable,
    rulingPlanet: 'Mercury',
    startDate: DateTime(2024, 8, 23),
    endDate: DateTime(2024, 9, 22),
  ),
  ZodiacSignType.libra: ZodiacSign(
    type: ZodiacSignType.libra,
    name: 'Libra',
    symbol: '♎',
    element: Element.air,
    modality: Modality.cardinal,
    rulingPlanet: 'Venus',
    startDate: DateTime(2024, 9, 23),
    endDate: DateTime(2024, 10, 22),
  ),
  ZodiacSignType.scorpio: ZodiacSign(
    type: ZodiacSignType.scorpio,
    name: 'Scorpio',
    symbol: '♏',
    element: Element.water,
    modality: Modality.fixed,
    rulingPlanet: 'Pluto',
    startDate: DateTime(2024, 10, 23),
    endDate: DateTime(2024, 11, 21),
  ),
  ZodiacSignType.sagittarius: ZodiacSign(
    type: ZodiacSignType.sagittarius,
    name: 'Sagittarius',
    symbol: '♐',
    element: Element.fire,
    modality: Modality.mutable,
    rulingPlanet: 'Jupiter',
    startDate: DateTime(2024, 11, 22),
    endDate: DateTime(2024, 12, 21),
  ),
  ZodiacSignType.capricorn: ZodiacSign(
    type: ZodiacSignType.capricorn,
    name: 'Capricorn',
    symbol: '♑',
    element: Element.earth,
    modality: Modality.cardinal,
    rulingPlanet: 'Saturn',
    startDate: DateTime(2024, 12, 22),
    endDate: DateTime(2024, 1, 19),
  ),
  ZodiacSignType.aquarius: ZodiacSign(
    type: ZodiacSignType.aquarius,
    name: 'Aquarius',
    symbol: '♒',
    element: Element.air,
    modality: Modality.fixed,
    rulingPlanet: 'Uranus',
    startDate: DateTime(2024, 1, 20),
    endDate: DateTime(2024, 2, 18),
  ),
  ZodiacSignType.pisces: ZodiacSign(
    type: ZodiacSignType.pisces,
    name: 'Pisces',
    symbol: '♓',
    element: Element.water,
    modality: Modality.mutable,
    rulingPlanet: 'Neptune',
    startDate: DateTime(2024, 2, 19),
    endDate: DateTime(2024, 3, 20),
  ),
};

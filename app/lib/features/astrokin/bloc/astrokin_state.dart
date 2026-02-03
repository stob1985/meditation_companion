import 'package:equatable/equatable.dart';
import '../models/models.dart';

enum AstroKinStatus {
  initial,
  loading,
  loaded,
  error,
}

class AstroKinState extends Equatable {
  final AstroKinStatus status;
  final Family? family;
  final FamilyEnergySnapshot? currentEnergy;
  final List<FamilyEnergySnapshot> energyHistory;
  final List<AstrologicalEvent> upcomingEvents;
  final List<AstrologicalEvent> todayEvents;
  final List<ParentingHack> parentingHacks;
  final ParentingHack? dailyHack;
  final List<SiblingDynamic> siblingDynamics;
  final SiblingDynamic? selectedDynamic;
  final List<RetrogradeInfo> activeRetrogrades;
  final List<RetrogradeInfo> upcomingRetrogrades;
  final FamilyMember? selectedChild;
  final DateTime selectedDate;
  final String? errorMessage;

  AstroKinState({
    this.status = AstroKinStatus.initial,
    this.family,
    this.currentEnergy,
    this.energyHistory = const [],
    this.upcomingEvents = const [],
    this.todayEvents = const [],
    this.parentingHacks = const [],
    this.dailyHack,
    this.siblingDynamics = const [],
    this.selectedDynamic,
    this.activeRetrogrades = const [],
    this.upcomingRetrogrades = const [],
    this.selectedChild,
    DateTime? selectedDate,
    this.errorMessage,
  }) : selectedDate = selectedDate ?? DateTime.now();

  bool get hasFamily => family != null;
  bool get hasMembers => family != null && family!.members.isNotEmpty;
  bool get hasChildren => family != null && family!.hasChildren;
  bool get hasMultipleChildren => family != null && family!.hasMultipleChildren;
  bool get isLoading => status == AstroKinStatus.loading;
  bool get hasError => status == AstroKinStatus.error;
  bool get isRetrogradActive => activeRetrogrades.isNotEmpty;

  List<FamilyMember> get children => family?.children ?? [];
  List<FamilyMember> get parents => family?.parents ?? [];

  AstroKinState copyWith({
    AstroKinStatus? status,
    Family? family,
    FamilyEnergySnapshot? currentEnergy,
    List<FamilyEnergySnapshot>? energyHistory,
    List<AstrologicalEvent>? upcomingEvents,
    List<AstrologicalEvent>? todayEvents,
    List<ParentingHack>? parentingHacks,
    ParentingHack? dailyHack,
    List<SiblingDynamic>? siblingDynamics,
    SiblingDynamic? selectedDynamic,
    List<RetrogradeInfo>? activeRetrogrades,
    List<RetrogradeInfo>? upcomingRetrogrades,
    FamilyMember? selectedChild,
    DateTime? selectedDate,
    String? errorMessage,
    bool clearError = false,
    bool clearDailyHack = false,
    bool clearSelectedDynamic = false,
    bool clearSelectedChild = false,
  }) {
    return AstroKinState(
      status: status ?? this.status,
      family: family ?? this.family,
      currentEnergy: currentEnergy ?? this.currentEnergy,
      energyHistory: energyHistory ?? this.energyHistory,
      upcomingEvents: upcomingEvents ?? this.upcomingEvents,
      todayEvents: todayEvents ?? this.todayEvents,
      parentingHacks: parentingHacks ?? this.parentingHacks,
      dailyHack: clearDailyHack ? null : (dailyHack ?? this.dailyHack),
      siblingDynamics: siblingDynamics ?? this.siblingDynamics,
      selectedDynamic: clearSelectedDynamic ? null : (selectedDynamic ?? this.selectedDynamic),
      activeRetrogrades: activeRetrogrades ?? this.activeRetrogrades,
      upcomingRetrogrades: upcomingRetrogrades ?? this.upcomingRetrogrades,
      selectedChild: clearSelectedChild ? null : (selectedChild ?? this.selectedChild),
      selectedDate: selectedDate ?? this.selectedDate,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }

  @override
  List<Object?> get props => [
        status,
        family,
        currentEnergy,
        energyHistory,
        upcomingEvents,
        todayEvents,
        parentingHacks,
        dailyHack,
        siblingDynamics,
        selectedDynamic,
        activeRetrogrades,
        upcomingRetrogrades,
        selectedChild,
        selectedDate,
        errorMessage,
      ];
}

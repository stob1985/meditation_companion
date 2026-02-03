import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/astrokin_repository.dart';
import 'astrokin_event.dart';
import 'astrokin_state.dart';

class AstroKinBloc extends Bloc<AstroKinEvent, AstroKinState> {
  final AstroKinRepository _repository;

  AstroKinBloc({required AstroKinRepository repository})
      : _repository = repository,
        super(AstroKinState()) {
    on<LoadFamily>(_onLoadFamily);
    on<CreateFamily>(_onCreateFamily);
    on<AddFamilyMember>(_onAddFamilyMember);
    on<UpdateFamilyMember>(_onUpdateFamilyMember);
    on<RemoveFamilyMember>(_onRemoveFamilyMember);
    on<LoadFamilyEnergy>(_onLoadFamilyEnergy);
    on<LoadEnergyHistory>(_onLoadEnergyHistory);
    on<LoadUpcomingEvents>(_onLoadUpcomingEvents);
    on<LoadEventsForDate>(_onLoadEventsForDate);
    on<LoadParentingHacks>(_onLoadParentingHacks);
    on<LoadDailyHack>(_onLoadDailyHack);
    on<LoadSiblingDynamics>(_onLoadSiblingDynamics);
    on<AnalyzeSiblings>(_onAnalyzeSiblings);
    on<LoadActiveRetrogrades>(_onLoadActiveRetrogrades);
    on<LoadUpcomingRetrogrades>(_onLoadUpcomingRetrogrades);
    on<LoadDashboard>(_onLoadDashboard);
    on<RefreshDashboard>(_onRefreshDashboard);
    on<SelectChild>(_onSelectChild);
    on<SelectDate>(_onSelectDate);
  }

  Future<void> _onLoadFamily(LoadFamily event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      final family = await _repository.getFamily();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onCreateFamily(CreateFamily event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      final family = await _repository.createFamily(event.name);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onAddFamilyMember(AddFamilyMember event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      await _repository.addFamilyMember(event.member);
      final family = await _repository.getFamily();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onUpdateFamilyMember(UpdateFamilyMember event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      await _repository.updateFamilyMember(event.member);
      final family = await _repository.getFamily();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onRemoveFamilyMember(RemoveFamilyMember event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      await _repository.removeFamilyMember(event.memberId);
      final family = await _repository.getFamily();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadFamilyEnergy(LoadFamilyEnergy event, Emitter<AstroKinState> emit) async {
    try {
      final energy = await _repository.getFamilyEnergy(event.date ?? DateTime.now());
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        currentEnergy: energy,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadEnergyHistory(LoadEnergyHistory event, Emitter<AstroKinState> emit) async {
    try {
      final history = await _repository.getEnergyHistory(event.startDate, event.endDate);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        energyHistory: history,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadUpcomingEvents(LoadUpcomingEvents event, Emitter<AstroKinState> emit) async {
    try {
      final events = await _repository.getUpcomingEvents(days: event.days);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        upcomingEvents: events,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadEventsForDate(LoadEventsForDate event, Emitter<AstroKinState> emit) async {
    try {
      final events = await _repository.getEventsForDate(event.date);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        todayEvents: events,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadParentingHacks(LoadParentingHacks event, Emitter<AstroKinState> emit) async {
    try {
      final hacks = await _repository.getParentingHacks(event.child);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        parentingHacks: hacks,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadDailyHack(LoadDailyHack event, Emitter<AstroKinState> emit) async {
    try {
      final hack = await _repository.getDailyHack(event.child);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        dailyHack: hack,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadSiblingDynamics(LoadSiblingDynamics event, Emitter<AstroKinState> emit) async {
    try {
      final dynamics = await _repository.getSiblingDynamics();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        siblingDynamics: dynamics,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onAnalyzeSiblings(AnalyzeSiblings event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      final dynamic = await _repository.analyzeSiblings(event.sibling1, event.sibling2);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        selectedDynamic: dynamic,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadActiveRetrogrades(LoadActiveRetrogrades event, Emitter<AstroKinState> emit) async {
    try {
      final retrogrades = await _repository.getActiveRetrogrades();
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        activeRetrogrades: retrogrades,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadUpcomingRetrogrades(LoadUpcomingRetrogrades event, Emitter<AstroKinState> emit) async {
    try {
      final retrogrades = await _repository.getUpcomingRetrogrades(days: event.days);
      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        upcomingRetrogrades: retrogrades,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onLoadDashboard(LoadDashboard event, Emitter<AstroKinState> emit) async {
    emit(state.copyWith(status: AstroKinStatus.loading));
    try {
      final family = await _repository.getFamily();
      final energy = await _repository.getFamilyEnergy(DateTime.now());
      final events = await _repository.getUpcomingEvents(days: 7);
      final todayEvents = await _repository.getEventsForDate(DateTime.now());
      final retrogrades = await _repository.getActiveRetrogrades();

      emit(state.copyWith(
        status: AstroKinStatus.loaded,
        family: family,
        currentEnergy: energy,
        upcomingEvents: events,
        todayEvents: todayEvents,
        activeRetrogrades: retrogrades,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: AstroKinStatus.error,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onRefreshDashboard(RefreshDashboard event, Emitter<AstroKinState> emit) async {
    add(LoadDashboard());
  }

  void _onSelectChild(SelectChild event, Emitter<AstroKinState> emit) {
    emit(state.copyWith(selectedChild: event.child));
  }

  void _onSelectDate(SelectDate event, Emitter<AstroKinState> emit) {
    emit(state.copyWith(selectedDate: event.date));
  }
}

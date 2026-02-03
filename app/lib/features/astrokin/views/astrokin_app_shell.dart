import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../theme/astrokin_theme.dart';
import 'dashboard_screen.dart';
import 'parenting_hacks_screen.dart';
import 'peace_calendar_screen.dart';
import 'sibling_dynamics_screen.dart';
import 'retrograde_kit_screen.dart';
import 'family_profile_screen.dart';

class AstroKinAppShell extends StatefulWidget {
  const AstroKinAppShell({super.key});

  @override
  State<AstroKinAppShell> createState() => _AstroKinAppShellState();
}

class _AstroKinAppShellState extends State<AstroKinAppShell> {
  int _currentIndex = 0;

  final List<_NavItem> _navItems = [
    _NavItem(
      icon: Icons.home_outlined,
      activeIcon: Icons.home,
      label: 'Home',
    ),
    _NavItem(
      icon: Icons.auto_awesome_outlined,
      activeIcon: Icons.auto_awesome,
      label: 'Tips',
    ),
    _NavItem(
      icon: Icons.calendar_month_outlined,
      activeIcon: Icons.calendar_month,
      label: 'Calendar',
    ),
    _NavItem(
      icon: Icons.people_outline,
      activeIcon: Icons.people,
      label: 'Siblings',
    ),
    _NavItem(
      icon: Icons.shield_outlined,
      activeIcon: Icons.shield,
      label: 'Retrograde',
    ),
  ];

  @override
  void initState() {
    super.initState();
    // Load initial data
    context.read<AstroKinBloc>().add(LoadDashboard());
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        return Scaffold(
          appBar: _buildAppBar(context, state),
          body: _buildBody(),
          bottomNavigationBar: _buildBottomNavigation(),
          drawer: _buildDrawer(context, state),
        );
      },
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context, AstroKinState state) {
    return AppBar(
      title: Text(_getTitle()),
      actions: [
        if (state.isRetrogradActive)
          Container(
            margin: const EdgeInsets.only(right: AstroKinSpacing.sm),
            padding: const EdgeInsets.symmetric(
              horizontal: AstroKinSpacing.sm,
              vertical: AstroKinSpacing.xs,
            ),
            decoration: BoxDecoration(
              color: AstroKinTheme.primaryPurple.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AstroKinRadius.md),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('☿', style: TextStyle(fontSize: 14)),
                const SizedBox(width: 4),
                Text(
                  'Rx',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AstroKinTheme.primaryPurple,
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ),
        IconButton(
          icon: const Icon(Icons.person_outline),
          onPressed: () => _navigateToProfile(context),
        ),
      ],
    );
  }

  String _getTitle() {
    switch (_currentIndex) {
      case 0:
        return 'AstroKin';
      case 1:
        return 'Parenting Tips';
      case 2:
        return 'Peace Calendar';
      case 3:
        return 'Sibling Dynamics';
      case 4:
        return 'Retrograde Kit';
      default:
        return 'AstroKin';
    }
  }

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return const DashboardScreen();
      case 1:
        return const ParentingHacksScreen();
      case 2:
        return const PeaceCalendarScreen();
      case 3:
        return const SiblingDynamicsScreen();
      case 4:
        return const RetrogradeKitScreen();
      default:
        return const DashboardScreen();
    }
  }

  Widget _buildBottomNavigation() {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: (index) {
        setState(() {
          _currentIndex = index;
        });
      },
      items: _navItems.map((item) {
        return BottomNavigationBarItem(
          icon: Icon(item.icon),
          activeIcon: Icon(item.activeIcon),
          label: item.label,
        );
      }).toList(),
    );
  }

  Widget _buildDrawer(BuildContext context, AstroKinState state) {
    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              decoration: const BoxDecoration(
                gradient: AstroKinTheme.primaryGradient,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(AstroKinSpacing.md),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(AstroKinRadius.md),
                        ),
                        child: const Icon(
                          Icons.auto_awesome,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                      const SizedBox(width: AstroKinSpacing.md),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'AstroKin',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          Text(
                            'Family Harmony Guide',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.white.withValues(alpha: 0.8),
                                ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  if (state.hasFamily) ...[
                    const SizedBox(height: AstroKinSpacing.md),
                    Container(
                      padding: const EdgeInsets.all(AstroKinSpacing.sm),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.family_restroom,
                            color: Colors.white,
                            size: 18,
                          ),
                          const SizedBox(width: AstroKinSpacing.sm),
                          Text(
                            state.family!.name,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Colors.white,
                                ),
                          ),
                          const Spacer(),
                          Text(
                            '${state.family!.memberCount} members',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.white.withValues(alpha: 0.8),
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Menu Items
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(AstroKinSpacing.md),
                children: [
                  _buildDrawerItem(
                    context,
                    icon: Icons.home_outlined,
                    label: 'Dashboard',
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _currentIndex = 0);
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.auto_awesome_outlined,
                    label: 'Parenting Tips',
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _currentIndex = 1);
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.calendar_month_outlined,
                    label: 'Peace Calendar',
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _currentIndex = 2);
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.people_outline,
                    label: 'Sibling Dynamics',
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _currentIndex = 3);
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.shield_outlined,
                    label: 'Retrograde Kit',
                    badge: state.isRetrogradActive ? 'Active' : null,
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _currentIndex = 4);
                    },
                  ),
                  const Divider(height: AstroKinSpacing.lg),
                  _buildDrawerItem(
                    context,
                    icon: Icons.family_restroom,
                    label: 'Family Profile',
                    onTap: () {
                      Navigator.pop(context);
                      _navigateToProfile(context);
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.settings_outlined,
                    label: 'Settings',
                    onTap: () {
                      Navigator.pop(context);
                      // Navigate to settings
                    },
                  ),
                  _buildDrawerItem(
                    context,
                    icon: Icons.help_outline,
                    label: 'Help & Support',
                    onTap: () {
                      Navigator.pop(context);
                      // Navigate to help
                    },
                  ),
                ],
              ),
            ),

            // Version
            Padding(
              padding: const EdgeInsets.all(AstroKinSpacing.md),
              child: Text(
                'AstroKin v1.0.0',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AstroKinTheme.textSecondary,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawerItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    String? badge,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(label),
      trailing: badge != null
          ? Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AstroKinSpacing.sm,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: AstroKinTheme.primaryPurple.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AstroKinRadius.sm),
              ),
              child: Text(
                badge,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AstroKinTheme.primaryPurple,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            )
          : null,
      onTap: onTap,
    );
  }

  void _navigateToProfile(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const FamilyProfileScreen(),
      ),
    );
  }
}

class _NavItem {
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _NavItem({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}

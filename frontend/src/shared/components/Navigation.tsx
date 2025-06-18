import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useAppDispatch } from '@/features/auth/hooks/useAuth';
import { logout } from '@/features/auth/slice';

export const Navigation = () => {
  const { user } = useAuth();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname.startsWith(path);

  const linkClasses = (active: boolean) =>
    `px-3 py-2 rounded-md text-sm font-medium ${active ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'}`;

  const isBuddy = (() => {
    const checkStr = (val: string) => {
      if (!val) return false;
      const v = val.toLowerCase();
      return v === 'buddy' || v === 'бадди';
    };

    if (checkStr((user as any)?.role ?? '')) return true;
    if ((user as any)?.is_buddy === true) return true;

    const rolesField = (user as any)?.roles;
    if (Array.isArray(rolesField)) {
      return rolesField.some((r: any) => {
        if (!r) return false;
        if (typeof r === 'string') return checkStr(r);
        return (
          checkStr(r.name || '') ||
          checkStr(r.slug || '') ||
          checkStr(r.display_name || '')
        );
      });
    }
    return false;
  })();

  return (
    <nav className="bg-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-white font-bold">BuddyBot</span>
            </div>
            <div className="hidden md:flex ml-10 space-x-4">
              <Link to="/" className={linkClasses(isActive('/'))}>
                Мои потоки
              </Link>
              <Link
                to="/buddy/dashboard"
                className={linkClasses(isActive('/buddy/dashboard')) + (!isBuddy ? ' opacity-60' : '')}
              >
                Панель бадди
              </Link>
              <Link
                to="/buddy/assign-flow"
                className={linkClasses(isActive('/buddy/assign-flow')) + (!isBuddy ? ' opacity-60' : '')}
              >
                Назначить поток
              </Link>
            </div>
          </div>
          
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              <div className="text-gray-300 text-sm flex items-center space-x-2">
                <span>{user?.name}</span>
                {isBuddy && (
                  <span className="px-2 py-1 text-xs bg-blue-500 text-white rounded-full">Бадди</span>
                )}
                <button
                  onClick={() => {
                    dispatch(logout());
                    navigate('/auth');
                  }}
                  className="ml-4 text-gray-300 hover:text-white text-sm"
                >
                  Выйти
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Мобильное меню */}
      <div className="md:hidden">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <Link to="/" className={`block ${linkClasses(isActive('/'))}`}>Мои потоки</Link>
          <Link to="/buddy/dashboard" className={`block ${linkClasses(isActive('/buddy/dashboard'))} ${!isBuddy ? 'opacity-60' : ''}`}>Панель бадди</Link>
          <Link to="/buddy/assign-flow" className={`block ${linkClasses(isActive('/buddy/assign-flow'))} ${!isBuddy ? 'opacity-60' : ''}`}>Назначить поток</Link>
          <button
            onClick={() => {
              dispatch(logout());
              navigate('/auth');
            }}
            className={`block w-full text-left ${linkClasses(false)}`}
          >
            Выйти
          </button>
        </div>
      </div>
    </nav>
  );
}; 
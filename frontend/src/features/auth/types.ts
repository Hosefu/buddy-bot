export interface User {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  roles: string[];
}

export interface Tokens {
  access: string;
  refresh: string;
}

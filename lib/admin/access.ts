const ACCESS_EMAIL_HEADER = "cf-access-authenticated-user-email";

export function isAuthorizedAdminEmail(headers: Headers, configuredEmail: string | null | undefined) {
  const expected = configuredEmail?.trim().toLowerCase();
  const actual = headers.get(ACCESS_EMAIL_HEADER)?.trim().toLowerCase();
  return Boolean(expected && actual && actual === expected);
}

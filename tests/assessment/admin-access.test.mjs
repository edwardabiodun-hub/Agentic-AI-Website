import assert from "node:assert/strict";
import test from "node:test";
import { isAuthorizedAdminEmail } from "../../lib/admin/access.ts";

test("admin access requires a configured admin email and matching Cloudflare Access email header", () => {
  const headers = new Headers({
    "cf-access-authenticated-user-email": "Edward.Abiodun@RunRateGroup.com",
  });

  assert.equal(
    isAuthorizedAdminEmail(headers, "edward.abiodun@runrategroup.com"),
    true,
  );
});

test("admin access fails closed when the Cloudflare Access email header is absent or mismatched", () => {
  assert.equal(
    isAuthorizedAdminEmail(new Headers(), "edward.abiodun@runrategroup.com"),
    false,
  );
  assert.equal(
    isAuthorizedAdminEmail(
      new Headers({
        "cf-access-authenticated-user-email": "someone@example.com",
      }),
      "edward.abiodun@runrategroup.com",
    ),
    false,
  );
  assert.equal(
    isAuthorizedAdminEmail(
      new Headers({
        "cf-access-authenticated-user-email": "edward.abiodun@runrategroup.com",
      }),
      "",
    ),
    false,
  );
});

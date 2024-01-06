# """Tests for the sensor module."""

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from pytest_homeassistant.async_mock import AsyncMock, MagicMock, Mock

# from custom_components.sma_charge_ctrl.sensor import ModbusClientSensor, ModbusRegisterSensor

# async def test_async_update_success(hass, aioclient_mock):
#     """Tests a fully successful async_update."""
#     github = MagicMock()
#     github.getitem = AsyncMock(
#         side_effect=[
#             # repos response
#             {
#                 "forks_count": 1000,
#                 "name": "Home Assistant",
#                 "permissions": {"admin": False, "push": True, "pull": False},
#                 "stargazers_count": 9000,
#             },
#             # clones response
#             {"count": 100, "uniques": 50},
#             # views response
#             {"count": 10000, "uniques": 5000},
#             # commits response
#             [
#                 {
#                     "commit": {"message": "Did a thing."},
#                     "sha": "e751664d95917dbdb856c382bfe2f4655e2a83c1",
#                 }
#             ],
#             # pulls response
#             [{"html_url": "https://github.com/homeassistant/core/pull/1347"}],
#             # issues response
#             [{"html_url": "https://github.com/homeassistant/core/issues/1"}],
#             # releases response
#             [{"html_url": "https://github.com/homeassistant/core/releases/v0.1.112"}],
#         ]
#     )
#     link = 'Link: <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=2>; rel="next", <https://api.github.com/repositories/12888993/issues?per_page=1&state=open&page=100>; rel="last"'
#     # This odd mock is to mock the async with in the `_get_total` method.
#     github._session.get.return_value.__aenter__ = AsyncMock(
#         return_value=Mock(headers={"Link": link})
#     )
#     sensor = ModbusClientSensor(github, {"path": "homeassistant/core"})
#     await sensor.async_update()

#     assert sensor.available is True


# async def test_async_update_failed():
#     """Tests a failed async_update."""
#     github = MagicMock()
#     github.getitem = AsyncMock(side_effect=GitHubException)

#     sensor = GitHubRepoSensor(github, {"path": "homeassistant/core"})
#     await sensor.async_update()

#     assert sensor.available is False
#     assert {"path": "homeassistant/core"} == sensor.attrs


